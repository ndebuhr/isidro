import json
import metrics
import os
import requests

from flask import Flask, abort, request
from mongo import confirmations_collection
from prometheus_client import generate_latest

CONFIRMATION_WORDS = [
    "yes",
    "yeah",
    "yup",
    "y",
    "correct",
    "confirm",
    "sure",
    "ok",
    "okay",
]

app = Flask(__name__)


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
                "text": self.action["confirmation message"],
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

    def is_link(self):
        return self.action["category"] == "link"

    def send_response(self):
        if self.is_link():
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
        # TODO: Cover additional synchronous task cases


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
