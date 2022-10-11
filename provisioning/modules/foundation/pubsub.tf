resource "google_pubsub_topic" "requests" {
  name = "isidro-requests"
  # 24 hour message retention
  message_retention_duration = "86600s"
  depends_on                 = [google_pubsub_schema.requests]
  schema_settings {
    schema   = "projects/${var.project_id}/schemas/isidro-requests"
    encoding = "JSON"
  }
}

resource "google_pubsub_schema" "requests" {
  name       = "isidro-requests"
  type       = "AVRO"
  definition = <<EOT
{
    "type" : "record",
    "name" : "isidro_requests",
    "fields" : [
        {
            "name" : "platform",
            "type" : "string"
        },
        {
            "name" : "channel",
            "type" : "string"
        },
        {
            "name" : "thread_ts",
            "type" : "string"
        },
        {
            "name" : "user",
            "type" : "string"
        },
        {
            "name" : "text",
            "type" : "string"
        }
    ]
}
EOT
}

resource "google_pubsub_subscription" "bigquery" {
  name  = "isidro-requests-datastream"
  topic = google_pubsub_topic.requests.name

  bigquery_config {
    table            = "${google_bigquery_table.requests.project}:${google_bigquery_table.requests.dataset_id}.${google_bigquery_table.requests.table_id}"
    use_topic_schema = true
    write_metadata   = true
  }

  depends_on = [google_project_iam_member.viewer, google_project_iam_member.editor]
}

resource "google_project_iam_member" "viewer" {
  project = var.project_id
  role    = "roles/bigquery.metadataViewer"
  member  = "serviceAccount:service-${var.project_number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:service-${var.project_number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

resource "google_bigquery_table" "requests" {
  deletion_protection = false
  table_id            = "requests"
  dataset_id          = google_bigquery_dataset.isidro.dataset_id

  time_partitioning {
    field = "publish_time"
    type  = "DAY"
  }

  schema = <<EOF
[
  {
    "name": "subscription_name",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "message_id",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "publish_time",
    "type": "TIMESTAMP",
    "mode": "NULLABLE"
  },
  {
    "name": "attributes",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "platform",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "channel",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "thread_ts",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "user",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "text",
    "type": "STRING",
    "mode": "NULLABLE"
  }
]
EOF
}

resource "google_pubsub_subscription" "orchestration" {
  name                         = "isidro-requests-orchestration"
  topic                        = google_pubsub_topic.requests.name
  retain_acked_messages        = true
  ack_deadline_seconds         = 60
  enable_exactly_once_delivery = true
  depends_on                   = [google_project_iam_member.viewer, google_project_iam_member.editor]
}