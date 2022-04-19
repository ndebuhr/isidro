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


class Repeater:
    def __init__(self, request):
        request = request.get_json()
        self.platform = request["platform"]
        self.channel = request["channel"]
        self.thread_ts = request["thread_ts"]
        self.user = request["user"]
        self.text = request["text"]
        self.verb = request["action"]["verb"]
        self.endpoint = request["action"]["endpoint"]
        self.headers = request["action"]["headers"]
        self.payload = request["action"]["payload"]
        self.completion_message = request["action"]["completion message"]
        self.interpolations = {
            "${var.platform}": self.platform,
            "${var.channel}": self.channel,
            "${var.thread_ts}": self.thread_ts,
            "${var.user}": self.user,
            "${var.text}": self.text,
            "@isidro ": "",
        }

    def payload_interpolation(self, payload):
        if type(payload) is dict:
            for payload_key in payload.keys():
                payload[payload_key] = self.payload_interpolation(payload[payload_key])
        elif type(payload) is list:
            for i in range(len(payload)):
                payload[i] = self.payload_interpolation(payload[i])
        else:
            for interpolation in self.interpolations.keys():
                payload = payload.replace(
                    interpolation, self.interpolations[interpolation]
                )
        return payload

    def repeat_request(self):
        if type(self.payload) is not str:
            requests.request(
                self.verb,
                headers=self.headers,
                url=self.endpoint,
                json=self.payload_interpolation(self.payload),
            ).raise_for_status()
        else:
            requests.request(
                self.verb,
                headers=self.headers,
                url=self.endpoint,
                data=self.payload_interpolation(self.payload),
            ).raise_for_status()
        requests.post(
            f"http://responder/v1/respond",
            json={
                "platform": self.platform,
                "channel": self.channel,
                "thread_ts": self.thread_ts,
                "user": self.user,
                "text": self.completion_message,
            },
        ).raise_for_status()


@app.route("/v1/repeat", methods=["POST"])
def repeat():
    repeat = Repeater(request)
    repeat.repeat_request()
    return ""
