import json
import metrics
import os
import requests

from flask import Flask, abort, request
from mongo import confirmations_collection
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
from prometheus_client import generate_latest

CONFIRMATION_WORDS = [
    "yes",
    "yeah",
    "yup",
    "y",
    "correct",
    "confirm",
    "ok",
    "okay",
    "cool",
    "sure"
]

GREETING = os.environ.get("GREETING")

if not GREETING:
    raise ValueError("No GREETING environment variable set")

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
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()


class Orchestration:
    def __init__(self, request):
        request = request.get_json()
        self.platform = request["platform"]
        self.channel = request["channel"]
        self.thread_ts = request["thread_ts"]
        self.user = request["user"]
        self.text = request["text"]
        self.confirmed = False
        self.confirmation_text = None
        self.action = None

    def confirmation(self):
        confirmations = confirmations_collection()
        count = confirmations.count_documents({"thread_ts": self.thread_ts})
        if count == 0:
            self.confirmed = False
        else:
            self.confirmation_text = self.text
            confirmation = confirmations.find_one({"thread_ts": self.thread_ts})
            self.channel = confirmation["channel"]
            self.thread_ts = confirmation["thread_ts"]
            self.user = confirmation["user"]
            self.text = confirmation["text"]
            self.confirmed = True

    def user_is_confirming(self):
        stripped_confirmation_text = (
            self.confirmation_text.replace(",", "")
            .replace(";", "")
            .replace(".", "")
            .lower()
        )
        for yes in CONFIRMATION_WORDS:
            if yes in stripped_confirmation_text.split(" "):
                return True
        return False

    def send_confirmation(self):
        confirmations_collection().insert_one(
            {
                "channel": self.channel,
                "thread_ts": self.thread_ts,
                "user": self.user,
                "text": self.text,
            }
        )
        requests.post(
            f"http://responder/v1/respond",
            json={
                "platform": self.platform,
                "channel": self.channel,
                "thread_ts": self.thread_ts,
                "user": self.user,
                "text": "{0}  {1}".format(
                    GREETING,
                    self.action["confirmation message"]
                ),
            },
        ).raise_for_status()

    def send_rejection(self):
        requests.post(
            f"http://responder/v1/respond",
            json={
                "platform": self.platform,
                "channel": self.channel,
                "thread_ts": self.thread_ts,
                "user": self.user,
                "text": "That does not sound like a confirmation - I will not proceed",
            },
        ).raise_for_status()

    def get_action(self):
        response = requests.post(
            f"http://keywords/v1/keywords",
            json={
                "text": self.text,
            },
        )
        response.raise_for_status()
        keywords = response.json()
        response = requests.post(
            f"http://policy-agent/v1/data/isidro/routing/action",
            json={
                "input": {"keywords": keywords},
            },
        )
        response.raise_for_status()
        self.action = min(
            response.json()["result"], key=lambda result: result["tie break priority"]
        )

    def is_async(self):
        return self.action["async"]

    def send_task(self):
        payload = self.action
        payload["platform"] = self.platform
        payload["channel"] = self.channel
        payload["thread_ts"] = self.thread_ts
        payload["user"] = self.user
        requests.post(
            f"http://tasks/v1/tasks",
            json=payload,
        ).raise_for_status()

    def send_response(self):
        if self.action["category"] == "link":
            requests.post(
                f"http://responder/v1/respond",
                json={
                    "platform": self.platform,
                    "channel": self.channel,
                    "thread_ts": self.thread_ts,
                    "user": self.user,
                    "text": "[{0}]({1})".format(
                        self.action["completion message"],
                        self.action["href"],
                    ),
                },
            ).raise_for_status()
        elif self.action["category"] == "repeater":
            requests.post(
                f"http://repeater/v1/repeat",
                json={
                    "platform": self.platform,
                    "channel": self.channel,
                    "thread_ts": self.thread_ts,
                    "user": self.user,
                    "text": self.text,
                    "action": self.action,
                },
            ).raise_for_status()


@app.route("/v1/orchestrate", methods=["POST"])
def orchestrate():
    orchestration = Orchestration(request)
    orchestration.confirmation()
    if not orchestration.confirmed:
        orchestration.get_action()
        orchestration.send_confirmation()
        return ""
    elif orchestration.user_is_confirming():
        orchestration.get_action()
        if orchestration.is_async():
            orchestration.send_task()
        else:
            orchestration.send_response()
        return ""
    elif not orchestration.user_is_confirming():
        orchestration.send_rejection()
        return ""
    else:
        abort(400)


@app.route("/metrics")
def metrics():
    return generate_latest()
