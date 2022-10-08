from spanner import database
from prometheus_client import Gauge

db = database()

def channels():
    with db.snapshot() as snapshot:
        result = snapshot.execute_sql(f"SELECT COUNT(DISTINCT channel) FROM posts")
    return result.one()[0]


channels_metric = Gauge(
    "isidro:channels", "Number of channels containing Isidro conversations"
)
channels_metric.set_function(channels)


def threads():
    with db.snapshot() as snapshot:
        result = snapshot.execute_sql(f"SELECT COUNT(DISTINCT thread_ts) FROM posts")
    return result.one()[0]


threads_metric = Gauge("isidro:threads", "Number of Isidro conversations")
threads_metric.set_function(threads)


def users():
    with db.snapshot() as snapshot:
        result = snapshot.execute_sql(f"SELECT COUNT(DISTINCT user) FROM posts")
    return result.one()[0]


users_metric = Gauge(
    "isidro:users", "Number of users who have had Isidro conversations"
)
users_metric.set_function(users)
