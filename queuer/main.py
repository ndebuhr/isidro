import json
import os

import observability

from flask import Flask, abort, request
from google.cloud import pubsub_v1

PUBSUB_PROJECT = os.environ.get("PUBSUB_PROJECT")

if not PUBSUB_PROJECT:
    raise ValueError("No PUBSUB_PROJECT environment variable set")

app = Flask(__name__)
observability.setup(flask_app=app, requests_enabled=True)
publisher = pubsub_v1.PublisherClient()


class Queuer:
    def __init__(self, request):
        request = request.get_json()
        self.platform = request["platform"]
        self.channel = request["channel"]
        self.thread_ts = request["thread_ts"]
        self.user = request["user"]
        self.text = request["text"]

    def queue(self):
        publisher.publish(
            f"projects/{PUBSUB_PROJECT}/topics/isidro-requests",
            json.dumps(
                {
                    "platform": self.platform,
                    "channel": self.channel,
                    "thread_ts": self.thread_ts,
                    "user": self.user,
                    "text": self.text,
                }
            ).encode("utf-8"),
        )


@app.route("/v1/queue", methods=["POST"])
def queue():
    queuer = Queuer(request)
    queuer.queue()
    return ""


@app.route("/", methods=["GET"])
def health():
    return ""
