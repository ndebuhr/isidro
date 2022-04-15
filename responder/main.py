import json
import os
import requests

from flask import Flask, abort, request

SLACK_OAUTH_TOKEN = os.environ.get("SLACK_OAUTH_TOKEN")
MATTERMOST_ACCESS_TOKEN = os.environ.get("MATTERMOST_ACCESS_TOKEN")
ISIDRO_DOMAIN = os.environ.get("ISIDRO_DOMAIN")

app = Flask(__name__)

if not SLACK_OAUTH_TOKEN:
    raise ValueError("No SLACK_OAUTH_TOKEN environment variable set")
if not MATTERMOST_ACCESS_TOKEN:
    raise ValueError("No MATTERMOST_ACCESS_TOKEN environment variable set")
if not ISIDRO_DOMAIN:
    raise ValueError("No ISIDRO_DOMAIN environment variable set")


class Responder:
    def __init__(self, request):
        request = request.get_json()
        self.platform = request["platform"]
        self.channel = request["channel"]
        self.thread_ts = request["thread_ts"]
        self.user = request["user"]
        self.text = request["text"]

    def respond_mattermost(self):
        requests.post(
            f"https://{ISIDRO_DOMAIN}/api/v4/posts",
            json={
                "channel_id": self.channel,
                "message": f"@{self.user} {self.text}",
                "root_id": self.thread_ts,
            },
            headers={"Authorization": f"Bearer {MATTERMOST_ACCESS_TOKEN}"},
        ).raise_for_status()

    def respond_slack(self):
        requests.post(
            "https://slack.com/api/chat.postMessage",
            json={
                "channel": self.channel,
                "thread_ts": self.thread_ts,
                "text": f"<@{self.user}> {self.text}.",
            },
            headers={
                "Authorization": f"Bearer {SLACK_OAUTH_TOKEN}",
            },
        ).raise_for_status()

    def respond(self):
        if self.platform == "mattermost":
            self.respond_mattermost()
        elif self.platform == "slack":
            self.respond_slack()
        else:
            abort(500)


@app.route("/v1/respond", methods=["POST"])
def respond():
    responder = Responder(request)
    responder.respond()
    return ""
