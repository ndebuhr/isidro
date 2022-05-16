resource "google_service_account" "nodes" {
  account_id   = "isidro-nodes"
  display_name = "Isidro Nodes"
}

resource "google_project_iam_member" "nodes_artifact_reader" {
  project = data.google_project.project.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.nodes.email}"
}

resource "google_project_iam_member" "nodes_log_writer" {
  project = data.google_project.project.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.nodes.email}"
}

resource "google_project_iam_member" "nodes_metric_writer" {
  project = data.google_project.project.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.nodes.email}"
}

resource "google_project_iam_member" "nodes_metric_reader" {
  project = data.google_project.project.project_id
  role    = "roles/monitoring.viewer"
  member  = "serviceAccount:${google_service_account.nodes.email}"
}

resource "google_project_iam_member" "nodes_metadata_writer" {
  project = data.google_project.project.project_id
  role    = "roles/stackdriver.resourceMetadata.writer"
  member  = "serviceAccount:${google_service_account.nodes.email}"
}

resource "google_project_iam_member" "nodes_object_reader" {
  project = data.google_project.project.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.nodes.email}"
}
