data "google_project" "project" {}

resource "google_pubsub_topic" "gtm_stream" {
  name = "isidro-gtm-stream"
}