resource "google_monitoring_slo" "gatekeeper_latency" {
  service = "canonical-ist:proj-${data.google_project.project.number}-default-gatekeeper"

  slo_id = "gatekeeper-latency"
  display_name = "Isidro SLO for latency"

  goal = 0.9
  calendar_period = "DAY"

  basic_sli {
    latency {
      threshold = "1s"
    }
  }
}

resource "google_monitoring_slo" "gatekeeper_errors" {
  service = "canonical-ist:proj-${data.google_project.project.number}-default-gatekeeper"

  slo_id = "gatekeeper-errors"
  display_name = "Isidro SLO for errors"

  goal = 0.99
  calendar_period = "DAY"

  basic_sli {
    availability {}
  }
}

resource "google_monitoring_alert_policy" "usage_alerting" {
  display_name = "Isidro Usage Alerting"
  combiner     = "OR"
  conditions {
    display_name = "New chatbot conversations"
    condition_threshold {
      filter     = "metric.type=\"prometheus.googleapis.com/threads/gauge\" AND resource.type=\"prometheus_target\""
      duration   = "86400s"  # one day
      comparison = "COMPARISON_LT"
      threshold_value = "0.0001"  # More than 0.01% growth expected per day (3.7% per year)
      aggregations {
        alignment_period   = "86400s"  # one day
        per_series_aligner = "ALIGN_PERCENT_CHANGE"
      }
    }
  }
}
