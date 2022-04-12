from mongo import confirmations_collection
from prometheus_client import Gauge


def channels():
    confirmations = confirmations_collection()
    return len(confirmations.distinct("channel"))


channels_metric = Gauge(
    "channels", "Number of channels containing Isidro conversations"
)
channels_metric.set_function(channels)


def threads():
    confirmations = confirmations_collection()
    return len(confirmations.distinct("thread_ts"))


threads_metric = Gauge("threads", "Number of Isidro conversations")
threads_metric.set_function(threads)


def users():
    confirmations = confirmations_collection()
    return len(confirmations.distinct("user"))


users_metric = Gauge("users", "Number of users who have had Isidro conversations")
users_metric.set_function(users)
