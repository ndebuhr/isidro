import io
import json
import os
import random
import requests
import time
import zipfile

from celery import Celery, Task, current_app
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

CELERY_BACKEND = "redis://isidro-redis-master:6379"
CELERY_BROKER = "pyamqp://isidro:isidro@isidro-rabbitmq//"

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
RESPONDER_HOST = os.environ.get("RESPONDER_HOST")

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

tasks = Celery(
    "tasks",
    backend=CELERY_BACKEND,
    broker=CELERY_BROKER,
)

if not GITHUB_TOKEN:
    raise ValueError("No GITHUB_TOKEN environment variable set")


class Deployer:
    def __init__(self, request):
        request = request.get_json()
        self.platform = request["platform"]
        self.channel = request["channel"]
        self.thread_ts = request["thread_ts"]
        self.user = request["user"]
        self.repository = request["repository"]
        self.workflow = request["workflow"]
        self.ref = request["ref"]
        self.completion_message = request["completion message"]
        self.artifacts_to_read = request["artifacts to read"]

    def last_workflow_run(self):
        last_run = requests.get(
            f"https://api.github.com/repos/{self.repository}/actions/runs?per_page=1",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"Token {GITHUB_TOKEN}",
            },
        )
        last_run.raise_for_status()
        return last_run.json()

    def deploy(self):
        last_run = self.last_workflow_run()
        if len(last_run["workflow_runs"]) > 0:
            last_run_number = int(last_run["workflow_runs"][0]["run_number"])
        else:
            last_run_number = 0
        requests.post(
            f"https://api.github.com/repos/{self.repository}/actions/workflows/{self.workflow}/dispatches",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"Token {GITHUB_TOKEN}",
            },
            json={
                "ref": self.ref,
            },
        ).raise_for_status()
        # Get the new workflow run id, with up to 20 GET requests over ~5 seconds
        found_run_id = False
        for i in range(10, 0, -1):
            last_run = self.last_workflow_run()
            if last_run["workflow_runs"][0]["run_number"] > last_run_number:
                found_run_id = True
                poll_for_conclusion.delay(
                    platform=self.platform,
                    channel=self.channel,
                    thread_ts=self.thread_ts,
                    user=self.user,
                    completion_message=self.completion_message,
                    repository=self.repository,
                    run_id=last_run["workflow_runs"][0]["id"],
                    artifacts_to_read=self.artifacts_to_read,
                )
                break
            time.sleep(0.25)
        if not found_run_id:
            abort(500)


@app.route("/v1/deploy", methods=["POST"])
def deploy():
    deployer = Deployer(request)
    deployer.deploy()
    return ""


@app.route("/", methods=["GET"])
def health():
    return ""


@tasks.task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=30,
    retry_jitter=True,
    retry_backoff_max=240,
)
def poll_for_conclusion(
    platform,
    channel,
    thread_ts,
    user,
    completion_message,
    repository,
    run_id,
    artifacts_to_read,
):
    run = requests.get(
        f"https://api.github.com/repos/{repository}/actions/runs/{run_id}",
        headers={
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Token {GITHUB_TOKEN}",
        },
    )
    run.raise_for_status()
    run_json = run.json()
    if run_json["conclusion"] is None:
        raise RuntimeError(f"Workflow run {run_id} is still running")
    elif run_json["conclusion"] == "success":
        requests.post(
            f"http://{RESPONDER_HOST}/v1/respond",
            json={
                "platform": platform,
                "channel": channel,
                "thread_ts": thread_ts,
                "user": user,
                "text": 'The [workflow]({0}) completed with status "{1}" and conclusion "{2}"'.format(
                    f"https://github.com/{repository}/actions/runs/{run_id}",
                    run_json["status"].upper(),
                    run_json["conclusion"].upper(),
                )
                if platform == "mattermost"
                else 'The workflow completed with status "{1}" and conclusion "{2}"'.format(
                    f"https://github.com/{repository}/actions/runs/{run_id}",
                    run_json["status"].upper(),
                    run_json["conclusion"].upper(),
                ),
            },
        ).raise_for_status()
        requests.post(
            f"http://{RESPONDER_HOST}/v1/respond",
            json={
                "platform": platform,
                "channel": channel,
                "thread_ts": thread_ts,
                "user": user,
                "text": completion_message,
            },
        ).raise_for_status()
        artifacts = requests.get(
            f"https://api.github.com/repos/{repository}/actions/runs/{run_id}/artifacts",
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"Token {GITHUB_TOKEN}",
            },
        )
        artifacts.raise_for_status()
        for artifact in artifacts.json()["artifacts"]:
            if artifact["name"] in artifacts_to_read:
                artifact_to_read = requests.get(
                    artifact["archive_download_url"],
                    headers={
                        "Accept": "application/vnd.github.v3+json",
                        "Authorization": f"Token {GITHUB_TOKEN}",
                    },
                )
                artifact_to_read.raise_for_status()
                artifact_zip = zipfile.ZipFile(io.BytesIO(artifact_to_read.content))
                # Assumes only one file in the artifact zip
                artifact_file = artifact_zip.open(artifact_zip.infolist()[0])
                requests.post(
                    f"http://{RESPONDER_HOST}/v1/respond",
                    json={
                        "platform": platform,
                        "channel": channel,
                        "thread_ts": thread_ts,
                        "user": user,
                        "text": io.TextIOWrapper(artifact_file).read(),
                    },
                ).raise_for_status()
        return run_json["conclusion"]
    else:
        requests.post(
            f"http://{RESPONDER_HOST}/v1/respond",
            json={
                "platform": platform,
                "channel": channel,
                "thread_ts": thread_ts,
                "user": user,
                "text": 'The [workflow]({0}) completed with status "{1}" and conclusion "{2}"'.format(
                    f"https://github.com/{repository}/actions/runs/{run_id}",
                    run_json["status"].upper(),
                    run_json["conclusion"].upper(),
                )
                if platform == "mattermost"
                else 'The workflow completed with status "{1}" and conclusion "{2}"'.format(
                    f"https://github.com/{repository}/actions/runs/{run_id}",
                    run_json["status"].upper(),
                    run_json["conclusion"].upper(),
                ),
            },
        ).raise_for_status()
        return run_json["conclusion"]
