from prometheus_client import Gauge

def define_metrics(tasks):

    def deployments_scheduled():
        i = tasks.control.inspect()
        return sum([len(i.scheduled()[worker]) for worker in i.scheduled().keys()])


    deployments_scheduled_metric = Gauge(
        "isidro:deployments_scheduled", "Deployments that have an ETA or are scheduled for later processing"
    )
    deployments_scheduled_metric.set_function(deployments_scheduled)

    def deployments_active():
        i = tasks.control.inspect()
        return sum([len(i.active()[worker]) for worker in i.active().keys()])


    deployments_active_metric = Gauge(
        "isidro:deployments_active", "Deployments that are currently active"
    )
    deployments_active_metric.set_function(deployments_active)

    def deployments_reserved():
        i = tasks.control.inspect()
        return sum([len(i.reserved()[worker]) for worker in i.reserved().keys()])


    deployments_reserved_metric = Gauge(
        "isidro:deployments_reserved", "Deployments that have been claimed by workers"
    )
    deployments_reserved_metric.set_function(deployments_reserved)