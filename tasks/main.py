import json
import os
import random
import requests

import observability

from flask import Flask, abort, request

RESPONDER_HOST = os.environ.get("RESPONDER_HOST")
DEPLOYER_GITHUB_HOST = os.environ.get("DEPLOYER_GITHUB_HOST")

if not RESPONDER_HOST:
    raise ValueError("No RESPONDER_HOST environment variable set")
if not DEPLOYER_GITHUB_HOST:
    raise ValueError("No DEPLOYER_GITHUB_HOST environment variable set")

app = Flask(__name__)
observability.setup(flask_app=app, requests_enabled=True)


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
