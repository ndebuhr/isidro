# Opinionated approach to setting up OpenTelemetry-based distributed tracing

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
from opentelemetry.sdk.trace.export import SimpleSpanProcessor


def setup(flask_app=None, requests_enabled=False):
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(CloudTraceSpanExporter())
    )

    if requests_enabled:
        RequestsInstrumentor().instrument()
    if flask_app:
        FlaskInstrumentor().instrument_app(
            flask_app,
            # Exclude the root path, which is hit regularly for load balancer health checks
            # https://github.com/open-telemetry/opentelemetry-python-contrib/issues/1181
            # Assumes RFC1035 domains
            excluded_urls="^http[s]?:\/\/[A-Za-z0-9\-\.]+\/$",
        )
    set_global_textmap(CloudTraceFormatPropagator())

    return trace
