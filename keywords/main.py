import json
import os
import spacy
import time

from flask import Flask, abort, request
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.cloud_trace_propagator import (
    CloudTraceFormatPropagator,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

nlp = spacy.load("en_core_web_lg")

# https://universaldependencies.org/docs/u/pos/
POS_TAGS = ["PROPN", "NOUN", "VERB", "NUM", "SYM", "X"]

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

class Keywords:
    def __init__(self, request):
        self.text = request.get_json()["text"]

    def keywords(self):
        # Extract candidate words/phrases
        keywords = []
        for token in nlp(self.text):
            # Skip stop words
            if token.is_stop:
                continue
            # Collect lemma (lowercase) if there's a part of speech match
            if token.pos_ in POS_TAGS:
                keywords.append(token.lemma_.lower())
        # Deduplicate and publish results
        keywords = set(keywords)
        return json.dumps(list(keywords))


@app.route("/v1/keywords", methods=["POST"])
def keywords():
    keywords = Keywords(request)
    return keywords.keywords()


@app.route("/", methods=["GET"])
def health():
    return ""
