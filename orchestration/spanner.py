import os
import uuid

from google.cloud import spanner

SPANNER_INSTANCE_ID = os.environ.get("SPANNER_INSTANCE_ID")
SPANNER_DATABASE_ID = os.environ.get("SPANNER_DATABASE_ID")

if not SPANNER_INSTANCE_ID:
    raise ValueError("No SPANNER_INSTANCE_ID environment variable set")
if not SPANNER_DATABASE_ID:
    raise ValueError("No SPANNER_DATABASE_ID environment variable set")


def insert_post(transaction, channel, thread_ts, user, text):
    transaction.execute_update(
        f"""
        INSERT posts (id, updated_at, channel, thread_ts, user, text) VALUES
        (
            '{str(uuid.uuid4())}',
            PENDING_COMMIT_TIMESTAMP(),
            '{channel}',
            '{thread_ts}',
            '{user}',
            '{text}'
        )
        """
    )


def database():
    client = spanner.Client()
    return client.instance(SPANNER_INSTANCE_ID).database(SPANNER_DATABASE_ID)
