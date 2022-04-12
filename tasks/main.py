import json
import os
import random
import requests

from flask import Flask, abort, request

app = Flask(__name__)


class Task:
    def __init__(self, request):
        request = request.get_json()
        self.platform = request["platform"]
        self.channel = request["channel"]
        self.thread_ts = request["thread_ts"]
        self.user = request["user"]
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
        self.category = request["category"]
        self.repository = (
            request["repository"] if "repository" in request.keys() else None
        )
        self.workflow = request["workflow"] if "workflow" in request.keys() else None
        self.ref = request["ref"] if "ref" in request.keys() else None

    def submit(self):
        if self.initialization_message is not None:
            requests.post(
                f"http://responder/v1/respond",
                json={
                    "platform": self.platform,
                    "channel": self.channel,
                    "thread_ts": self.thread_ts,
                    "user": self.user,
                    "text": self.initialization_message,
                },
            ).raise_for_status()
        if self.category == "github actions":
            trigger = self.deploy_github()

    def deploy_github(self):
        requests.post(
            "http://deployer-github/v1/deploy",
            json={
                "repository": self.repository,
                "workflow": self.workflow,
                "ref": self.ref,
                "platform": self.platform,
                "channel": self.channel,
                "thread_ts": self.thread_ts,
                "user": self.user,
                "completion message": self.completion_message,
            },
        ).raise_for_status()


@app.route("/v1/tasks", methods=["POST"])
def task():
    task = Task(request)
    task.submit()
    return ""
