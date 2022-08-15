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

SLACK_OAUTH_TOKEN = os.environ.get("SLACK_OAUTH_TOKEN")
MATTERMOST_ACCESS_TOKEN = os.environ.get("MATTERMOST_ACCESS_TOKEN")
MATTERMOST_DOMAIN = os.environ.get("MATTERMOST_DOMAIN")

if not SLACK_OAUTH_TOKEN:
    raise ValueError("No SLACK_OAUTH_TOKEN environment variable set")
if not MATTERMOST_ACCESS_TOKEN:
    raise ValueError("No MATTERMOST_ACCESS_TOKEN environment variable set")
if not MATTERMOST_DOMAIN:
    raise ValueError("No MATTERMOST_DOMAIN environment variable set")

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


class Responder:
    def __init__(self, request):
        request = request.get_json()
        self.platform = request["platform"]
        self.channel = request["channel"]
        self.thread_ts = request["thread_ts"]
        self.user = request["user"]
        self.text = request["text"]

    def respond_mattermost(self):
        requests.post(
            f"https://{MATTERMOST_DOMAIN}/api/v4/posts",
            json={
                "channel_id": self.channel,
                "message": f"@{self.user} {self.text}",
                "root_id": self.thread_ts,
            },
            headers={"Authorization": f"Bearer {MATTERMOST_ACCESS_TOKEN}"},
        ).raise_for_status()

    def respond_slack(self):
        requests.post(
            "https://slack.com/api/chat.postMessage",
            json={
                "channel": self.channel,
                "thread_ts": self.thread_ts,
                "text": f"<@{self.user}> {self.text}",
                "parse": "none",
            },
            headers={
                "Authorization": f"Bearer {SLACK_OAUTH_TOKEN}",
            },
        ).raise_for_status()

    def respond(self):
        if self.platform == "mattermost":
            self.respond_mattermost()
        elif self.platform == "slack":
            self.respond_slack()
        else:
            abort(500)


@app.route("/v1/respond", methods=["POST"])
def respond():
    responder = Responder(request)
    responder.respond()
    return ""


@app.route("/", methods=["GET"])
def health():
    return ""
