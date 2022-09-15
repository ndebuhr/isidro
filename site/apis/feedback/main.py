import os
import uuid

from flask import Flask, abort, request
from google.cloud import spanner

API_TOKEN = os.environ.get("API_TOKEN")
SPANNER_INSTANCE_ID = os.environ.get("SPANNER_INSTANCE_ID")
SPANNER_DATABASE_ID = os.environ.get("SPANNER_DATABASE_ID")

if not API_TOKEN:
    raise ValueError("No API_TOKEN environment variable set")
if not SPANNER_INSTANCE_ID:
    raise ValueError("No SPANNER_INSTANCE_ID environment variable set")
if not SPANNER_DATABASE_ID:
    raise ValueError("No SPANNER_DATABASE_ID environment variable set")

app = Flask(__name__)


def create_submission(transaction, record):
    transaction.execute_update(
        f"""
        INSERT submissions (EntryTimestamp, UserType, JobRole, Feedback) VALUES
        (
            PENDING_COMMIT_TIMESTAMP(),
            '{record["user-type"]}',
            '{record["job-type"]}',
            '{record["feedback"]}'
        )
        """
    )


def database():
    client = spanner.Client()
    return client.instance(SPANNER_INSTANCE_ID).database(SPANNER_DATABASE_ID)


@app.route("/v1/feedback", methods=["POST"])
def feedback():
    if not "Authorization" in request.headers:
        # Authorization header not provided
        abort(403)
    if len(request.headers.get("Authorization").split()) < 2:
        # Authorization header is malformed
        abort(403)
    if request.headers.get("Authorization").split()[1] != API_TOKEN:
        # Incorrect token provided
        abort(403)
    database().run_in_transaction(create_submission, request.get_json())
    return ""
