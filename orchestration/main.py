import json
import os
import re
import requests

import metrics
import trace

from flask import Flask, abort, request
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from spanner import database, insert_post
from prometheus_client import generate_latest

CONFIRMATION_WORDS = [
    "yes",
    "yeah",
    "yup",
    "y",
    "correct",
    "confirm",
    "ok",
    "okay",
    "sure",
]

GREETING = os.environ.get("GREETING")
RESPONDER_HOST = os.environ.get("RESPONDER_HOST")
KEYWORDS_HOST = os.environ.get("KEYWORDS_HOST")
GBASH_HOST = os.environ.get("GBASH_HOST")
KUBEBASH_HOST = os.environ.get("KUBEBASH_HOST")
POLICY_AGENT_HOST = os.environ.get("POLICY_AGENT_HOST")
TASKS_HOST = os.environ.get("TASKS_HOST")
REPEATER_HOST = os.environ.get("REPEATER_HOST")

if not GREETING:
    raise ValueError("No GREETING environment variable set")
if not RESPONDER_HOST:
    raise ValueError("No RESPONDER_HOST environment variable set")
if not KEYWORDS_HOST:
    raise ValueError("No KEYWORDS_HOST environment variable set")
if not GBASH_HOST:
    raise ValueError("No GBASH_HOST environment variable set")
if not KUBEBASH_HOST:
    raise ValueError("No KUBEBASH_HOST environment variable set")
if not POLICY_AGENT_HOST:
    raise ValueError("No POLICY_AGENT_HOST environment variable set")
if not TASKS_HOST:
    raise ValueError("No TASKS_HOST environment variable set")
if not REPEATER_HOST:
    raise ValueError("No REPEATER_HOST environment variable set")

app = Flask(__name__)
# Exclude the root path, which is hit regularly for load balancer health checks
# https://github.com/open-telemetry/opentelemetry-python-contrib/issues/1181
# Assumes RFC1035 domains
FlaskInstrumentor().instrument_app(app, excluded_urls="^http[s]?:\/\/[A-Za-z0-9\-\.]+\/$")
RequestsInstrumentor().instrument()


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
        db = database()
        with db.snapshot() as snapshot:
            thread = snapshot.execute_sql(
                f"""
                SELECT * FROM posts
                WHERE thread_ts='{self.thread_ts}'
                ORDER BY updated_at DESC
                """
            )
        post_count = 0
        for post in thread:
            post_count += 1
        if post_count == 0:
            raise Exception("Post was not successfully logged in the database")
        elif post_count == 1:
            self.confirmed = False
        else:
            self.confirmation_text = self.text
            self.channel = post[2]
            self.thread_ts = post[3]
            self.user = post[4]
            self.text = post[5]
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

    def insert_post(self):
        db = database()
        db.run_in_transaction(
            insert_post, self.channel, self.thread_ts, self.user, self.text
        )

    def send_rejection(self):
        self.send_message(
            "That does not sound like a confirmation - I will not proceed"
        )

    def get_action(self):
        response = requests.post(
            f"http://{KEYWORDS_HOST}/v1/keywords",
            json={
                "text": self.text,
            },
        )
        response.raise_for_status()
        keywords = response.json()
        response = requests.post(
            f"http://{POLICY_AGENT_HOST}/v1/data/isidro/routing/action",
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
        self.send_initialization()
        payload = self.action
        payload["platform"] = self.platform
        payload["channel"] = self.channel
        payload["thread_ts"] = self.thread_ts
        payload["user"] = self.user
        requests.post(
            f"http://{TASKS_HOST}/v1/tasks",
            json=payload,
        ).raise_for_status()
        # Completion messages are deferred to the task runner

    def is_link(self):
        return self.action["category"] == "link"

    def send_link(self):
        self.send_initialization()
        if self.platform == "mattermost":
            self.send_message(
                "[{0}]({1})".format(self.action["message"], self.action["href"])
            )
            self.send_completion()
        if self.platform == "slack":
            self.send_message(
                "<{1}|{0}>".format(self.action["message"], self.action["href"])
            )
            self.send_completion()

    def is_repeater(self):
        return self.action["category"] == "repeater"

    def send_repeater(self):
        self.send_initialization()
        requests.post(
            f"http://{REPEATER_HOST}/v1/repeat",
            json={
                "platform": self.platform,
                "channel": self.channel,
                "thread_ts": self.thread_ts,
                "user": self.user,
                "text": self.text,
                "action": self.action,
            },
        ).raise_for_status()
        # Completion messages are deferred to the repeater

    def is_kubebash(self):
        return self.action["category"] == "kubebash"

    def send_kubebash(self):
        self.send_initialization()
        if "interpolations" in self.action.keys():
            command = self.interpolate(
                self.text, self.action["command"], self.action["interpolations"]
            )
        else:
            command = self.action["command"]
        requests.post(
            f"http://{KUBEBASH_HOST}/hooks/kubebash", json={"command": command}
        ).raise_for_status()
        self.send_completion()

    def is_gbash(self):
        return self.action["category"] == "gbash"

    def send_gbash(self):
        self.send_initialization()
        if "interpolations" in self.action.keys():
            command = self.interpolate(
                self.text, self.action["command"], self.action["interpolations"]
            )
        else:
            command = self.action["command"]
        requests.post(
            f"http://{GBASH_HOST}/hooks/gbash", json={"command": command}
        ).raise_for_status()
        self.send_completion()

    def send_confirmation(self):
        if "confirmation interpolations" in self.action.keys():
            self.action["confirmation message"] = self.interpolate(
                self.text,
                self.action["confirmation message"],
                self.action["confirmation interpolations"],
            )
        self.send_message(
            "{0}  {1}".format(GREETING, self.action["confirmation message"])
        )

    def send_initialization(self):
        if "initialization message" in self.action.keys():
            if "initialization interpolations" in self.action.keys():
                self.action["initialization message"] = self.interpolate(
                    self.text,
                    self.action["initialization message"],
                    self.action["initialization interpolations"],
                )
            self.send_message(self.action["initialization message"])

    def send_completion(self):
        if "completion message" in self.action.keys():
            if "completion interpolations" in self.action.keys():
                self.action["completion message"] = self.interpolate(
                    self.text,
                    self.action["completion message"],
                    self.action["completion interpolations"],
                )
            self.send_message(self.action["completion message"])

    def send_message(self, message):
        requests.post(
            f"http://{RESPONDER_HOST}/v1/respond",
            json={
                "platform": self.platform,
                "channel": self.channel,
                "thread_ts": self.thread_ts,
                "user": self.user,
                "text": message,
            },
        ).raise_for_status()

    def interpolate(self, input_message, output_message, regex_expressions):
        for i, expression in enumerate(regex_expressions):
            replacement = re.findall(expression, input_message)
            if len(replacement) == 0:
                self.fail_interpolation()
            output_message = output_message.replace(
                "{" + str(i) + "}", str(replacement[0])
            )
        return output_message

    def fail_interpolation(self):
        if "interpolation failure message" in self.action.keys():
            self.send_message(self.action["interpolation failure message"])
        abort(400)


@app.route("/v1/orchestrate", methods=["POST"])
def orchestrate():
    orchestration = Orchestration(request)
    orchestration.insert_post()
    orchestration.confirmation()
    if not orchestration.confirmed:
        orchestration.get_action()
        orchestration.send_confirmation()
        return ""
    elif orchestration.user_is_confirming():
        orchestration.get_action()
        if orchestration.is_async():
            orchestration.send_task()
        elif orchestration.is_link():
            orchestration.send_link()
        elif orchestration.is_repeater():
            orchestration.send_repeater()
        elif orchestration.is_kubebash():
            orchestration.send_kubebash()
        elif orchestration.is_gbash():
            orchestration.send_gbash()
        return ""
    elif not orchestration.user_is_confirming():
        orchestration.send_rejection()
        return ""
    else:
        abort(400)


@app.route("/metrics")
def metrics():
    return generate_latest()


@app.route("/", methods=["GET"])
def health():
    return ""
