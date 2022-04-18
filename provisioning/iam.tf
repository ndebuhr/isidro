resource "google_service_account" "isidro_nodes" {
  account_id   = "isidro-nodes"
  display_name = "Isidro Nodes"
}

resource "google_project_iam_member" "artifact_reader" {
  project = data.google_project.project.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.isidro_nodes.email}"
}

resource "google_project_iam_member" "log_writer" {
  project = data.google_project.project.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.isidro_nodes.email}"
}

resource "google_project_iam_member" "metric_writer" {
  project = data.google_project.project.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.isidro_nodes.email}"
}

resource "google_project_iam_member" "metric_reader" {
  project = data.google_project.project.project_id
  role    = "roles/monitoring.viewer"
  member  = "serviceAccount:${google_service_account.isidro_nodes.email}"
}

resource "google_project_iam_member" "metadata_writer" {
  project = data.google_project.project.project_id
  role    = "roles/stackdriver.resourceMetadata.writer"
  member  = "serviceAccount:${google_service_account.isidro_nodes.email}"
}

resource "google_project_iam_member" "object_reader" {
  project = data.google_project.project.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.isidro_nodes.email}"
}

resource "google_service_account" "isidro_microservices" {
  account_id   = "isidro-microservices"
  display_name = "Isidro Microservice"
}

resource "google_project_iam_member" "trace_writer" {
  project = data.google_project.project.project_id
  role    = "roles/cloudtrace.agent"
  member  = "serviceAccount:${google_service_account.isidro_microservices.email}"
}

resource "google_project_iam_member" "workload_identity_user" {
  project = data.google_project.project.project_id
  role    = "roles/iam.workloadIdentityUser"
  member  = "serviceAccount:${data.google_project.project.project_id}.svc.id.goog[default/isidro-microservices]"
}