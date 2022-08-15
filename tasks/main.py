import json
import os
import random
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

RESPONDER_HOST = os.environ.get("RESPONDER_HOST")
DEPLOYER_GITHUB_HOST = os.environ.get("DEPLOYER_GITHUB_HOST")

if not RESPONDER_HOST:
    raise ValueError("No RESPONDER_HOST environment variable set")
if not DEPLOYER_GITHUB_HOST:
    raise ValueError("No DEPLOYER_GITHUB_HOST environment variable set")

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


class Task:
    def __init__(self, request):
        request = request.get_json()
        self.platform = request["platform"]
        self.channel = request["channel"]
        self.thread_ts = request["thread_ts"]
        self.user = request["user"]
        self.category = request["category"]
        self.repository = (
            request["repository"] if "repository" in request.keys() else None
        )
        self.workflow = request["workflow"] if "workflow" in request.keys() else None
        self.ref = request["ref"] if "ref" in request.keys() else None
        self.initialization_message = (
            request["initialization message"]
            if "initialization message" in request.keys()
            else None
        )
        self.completion_message = (
            request["completion message"]
            if "completion message" in request.keys()
            else None
        )
        self.artifacts_to_read = (
            request["artifacts to read"]
            if "artifacts to read" in request.keys()
            else []
        )

    def submit(self):
        if self.category == "github actions":
            trigger = self.deploy_github()

    def deploy_github(self):
        requests.post(
            f"http://{DEPLOYER_GITHUB_HOST}/v1/deploy",
            json={
                "platform": self.platform,
                "channel": self.channel,
                "thread_ts": self.thread_ts,
                "user": self.user,
                "repository": self.repository,
                "workflow": self.workflow,
                "ref": self.ref,
                "completion message": self.completion_message,
                "artifacts to read": self.artifacts_to_read,
            },
        ).raise_for_status()


@app.route("/v1/tasks", methods=["POST"])
def task():
    task = Task(request)
    task.submit()
    return ""


@app.route("/", methods=["GET"])
def health():
    return ""
