import functions_framework
import os

from concurrent import futures
from google.cloud import pubsub_v1
from typing import Callable

GOOGLE_PROJECT = os.environ.get("GOOGLE_PROJECT")
TOPIC_ID = "isidro-gtm-stream"
WEBSITE_ORIGIN = os.environ.get("WEBSITE_ORIGIN")

if not GOOGLE_PROJECT:
    raise ValueError("No GOOGLE_PROJECT environment variable set")
if not WEBSITE_ORIGIN:
    raise ValueError("No WEBSITE_ORIGIN environment variable set")

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(GOOGLE_PROJECT, TOPIC_ID)
# Async message publishing to avoid web clients choking up with timeouts, errors, etc.
publish_futures = []

# https://cloud.google.com/pubsub/docs/publisher#python
def get_callback(
    publish_future: pubsub_v1.publisher.futures.Future, data: str
) -> Callable[[pubsub_v1.publisher.futures.Future], None]:
    def callback(publish_future: pubsub_v1.publisher.futures.Future) -> None:
        try:
            # Wait 60 seconds for the publish call to succeed.
            print(publish_future.result(timeout=60))
        except futures.TimeoutError:
            print(f"Publishing {data} timed out.")

    return callback

@functions_framework.http
def to_pubsub(request):
    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        # Allows GET requests from the website origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': [WEBSITE_ORIGIN],
            'Access-Control-Allow-Methods': ['POST'],
            'Access-Control-Allow-Headers': ['Content-Type'],
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    publish_future = publisher.publish(topic_path, request.get_data())
    # Non-blocking. Publish failures are handled in the callback function.
    publish_future.add_done_callback(get_callback(publish_future, request.get_data()))
    publish_futures.append(publish_future)

    # Wait for all the publish futures to resolve before exiting.
    futures.wait(publish_futures, return_when=futures.ALL_COMPLETED)

    headers = {
        'Access-Control-Allow-Origin': [WEBSITE_ORIGIN],
        'Access-Control-Allow-Methods': ['POST'],
        'Access-Control-Allow-Headers': ['Content-Type'],
        'Access-Control-Max-Age': '3600'
    }

    return ('', 200, headers)