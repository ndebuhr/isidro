import os
import pymongo

from pymongo import MongoClient

MONGODB_HOST = os.environ.get("MONGODB_HOST")
MONGODB_USERNAME = os.environ.get("MONGODB_USERNAME")
MONGODB_PASSWORD = os.environ.get("MONGODB_PASSWORD")
MONGODB_DATABASE = os.environ.get("MONGODB_DATABASE")

if not MONGODB_HOST:
    raise ValueError("No MONGODB_HOST environment variable set")
if not MONGODB_USERNAME:
    raise ValueError("No MONGODB_USERNAME environment variable set")
if not MONGODB_PASSWORD:
    raise ValueError("No MONGODB_PASSWORD environment variable set")
if not MONGODB_DATABASE:
    raise ValueError("No MONGODB_DATABASE environment variable set")

CONNECTION_STRING = f"mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}"


def confirmations_collection():
    client = MongoClient(CONNECTION_STRING)
    return client[MONGODB_DATABASE]["confirmations"]
