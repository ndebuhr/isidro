import json
import os
import requests

from flask import Flask, abort, request
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.cloud_trace_propagator import (
    CloudTraceFormatPropagator,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

SLACK_VERIFICATION_TOKEN = os.environ.get("SLACK_VERIFICATION_TOKEN")
MATTERMOST_ACCESS_TOKEN = os.environ.get("MATTERMOST_ACCESS_TOKEN")
MATTERMOST_VERIFICATION_TOKEN = os.environ.get("MATTERMOST_VERIFICATION_TOKEN")
MATTERMOST_DOMAIN = os.environ.get("MATTERMOST_DOMAIN")
ORCHESTRATION_HOST = os.environ.get("ORCHESTRATION_HOST")

if not SLACK_VERIFICATION_TOKEN:
    raise ValueError("No SLACK_VERIFICATION_TOKEN environment variable set")
if not MATTERMOST_ACCESS_TOKEN:
    raise ValueError("No MATTERMOST_ACCESS_TOKEN environment variable set")
if not MATTERMOST_VERIFICATION_TOKEN:
    raise ValueError("No MATTERMOST_VERIFICATION_TOKEN environment variable set")
if not MATTERMOST_DOMAIN:
    raise ValueError("No MATTERMOST_DOMAIN environment variable set")
if not ORCHESTRATION_HOST:
    raise ValueError("No ORCHESTRATION_HOST environment variable set")

set_global_textmap(CloudTraceFormatPropagator())

tracer_provider = TracerProvider()
cloud_trace_exporter = CloudTraceSpanExporter()
tracer_provider.add_span_processor(
    # BatchSpanProcessor buffers spans and sends them in batches in a
    # background thread. The default parameters are sensible, but can be
    # tweaked to optimize your performance
    BatchSpanProcessor(cloud_trace_exporter)
)
trace.set_tracer_provider(tracer_provider)

tracer = trace.get_tracer(__name__)

app = Flask(__name__)
# Exclude the root path, which is hit regularly for load balancer health checks
# https://github.com/open-telemetry/opentelemetry-python-contrib/issues/1181
# Assumes RFC1035 domains
FlaskInstrumentor().instrument_app(app, excluded_urls="^http[s]?:\/\/[A-Za-z0-9\-\.]+\/$")
RequestsInstrumentor().instrument()


class Gatekeeper:
    def __init__(self, request):
        self.request = request

    def validate_json(self):
        if not self.request.is_json:
            abort(415)

    def validate_verification_token_provided(self):
        self.validate_json()
        if not "token" in self.request.get_json().keys():
            abort(403)

    def get_verification_token(self):
        return self.request.get_json()["token"]

    def validate_verification_token_correct(self):
        self.validate_verification_token_provided()
        if self.get_verification_token() not in [
            SLACK_VERIFICATION_TOKEN,
            MATTERMOST_VERIFICATION_TOKEN,
        ]:
            abort(403)

    def is_challenge_request(self):
        return "challenge" in self.request.get_json().keys()

    def get_platform(self):
        request_json = self.request.get_json()
        if "event" in request_json.keys():
            return "slack"
        else:
            return "mattermost"

    def get_channel(self):
        request_json = self.request.get_json()
        if "event" in request_json.keys() and "channel" in request_json["event"].keys():
            # Slack message
            return request_json["event"]["channel"]
        elif "channel_id" in request_json.keys():
            # Mattermost message
            return request_json["channel_id"]

    def get_thread_ts(self):
        request_json = self.request.get_json()
        if (
            "event" in request_json.keys()
            and "thread_ts" in request_json["event"].keys()
        ):
            # Threaded Slack message (continue thread)
            return request_json["event"]["thread_ts"]
        elif "event" in request_json.keys() and "ts" in request_json["event"].keys():
            # Initial Slack message (create thread)
            return request_json["event"]["ts"]
        elif "post_id" in request_json.keys():
            # Mattermost message (requires additional Mattermost API call to determine root_id)
            thread = requests.get(
                "https://{0}/api/v4/posts/{1}".format(
                    MATTERMOST_DOMAIN, request_json["post_id"]
                ),
                headers={"Authorization": f"Bearer {MATTERMOST_ACCESS_TOKEN}"},
            )
            thread.raise_for_status()
            thread_json = thread.json()
            if thread_json["root_id"] != "":
                return thread_json["root_id"]
            else:
                return request_json["post_id"]
        else:
            # Unknown message format
            abort(400)

    def get_user(self):
        request_json = self.request.get_json()
        if "event" in request_json.keys() and "user" in request_json["event"].keys():
            # Slack message
            return request_json["event"]["user"]
        elif "user_name" in request_json.keys():
            # Mattermost message
            return request_json["user_name"]
        else:
            # Unknown message format
            abort(400)

    def get_text(self):
        request_json = self.request.get_json()
        if "event" in request_json.keys() and "text" in request_json["event"].keys():
            # Slack message
            # Replace non-breaking spaces with regular spaces
            return request_json["event"]["text"].replace("\xa0", " ")
        elif "text" in request_json.keys():
            # Mattermost message
            return request_json["text"]
        else:
            # Unknown message format
            abort(400)

    def challenge_response(self):
        return self.request.get_json()["challenge"]

    def general_response(self):
        # Pass data to the orchestration service
        requests.post(
            f"http://{ORCHESTRATION_HOST}/v1/orchestrate",
            json={
                "platform": self.get_platform(),
                "channel": self.get_channel(),
                "thread_ts": self.get_thread_ts(),
                "user": self.get_user(),
                "text": self.get_text(),
            },
        ).raise_for_status()
        return ""


@app.route("/isidro/api/v1/submit", methods=["POST"])
def submission():
    gatekeeper = Gatekeeper(request)
    gatekeeper.validate_verification_token_correct()

    if gatekeeper.is_challenge_request():
        return gatekeeper.challenge_response()
    else:
        return gatekeeper.general_response()


@app.route("/", methods=["GET"])
def health():
    return ""


@app.after_request
def limit_slack_retries(response):
    response.headers["X-Slack-No-Retry"] = "1"
    return response
