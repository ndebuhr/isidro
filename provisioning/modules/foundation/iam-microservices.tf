resource "google_service_account" "tracing_microservices" {
  account_id   = "isidro-tracing-microservices"
  display_name = "Isidro Tracing Microservices"
}

resource "google_project_iam_member" "tracing_microservices_trace_writer" {
  project = var.project_id
  role    = "roles/cloudtrace.agent"
  member  = "serviceAccount:${google_service_account.tracing_microservices.email}"
}

resource "google_project_iam_member" "tracing_microservices_workload_identity_user" {
  project = var.project_id
  role    = "roles/iam.workloadIdentityUser"
  member  = "serviceAccount:${var.project_id}.svc.id.goog[isidro/tracing-microservice]"
}

resource "google_service_account" "db_microservices" {
  account_id   = "isidro-db-client-microservices"
  display_name = "Isidro DB Client Microservices"
}

resource "google_project_iam_member" "db_microservices_spanner_user" {
  project = var.project_id
  role    = "roles/spanner.databaseUser"
  member  = "serviceAccount:${google_service_account.db_microservices.email}"
}

resource "google_project_iam_member" "db_microservices_trace_writer" {
  project = var.project_id
  role    = "roles/cloudtrace.agent"
  member  = "serviceAccount:${google_service_account.db_microservices.email}"
}

resource "google_project_iam_member" "db_microservices_workload_identity_user" {
  project = var.project_id
  role    = "roles/iam.workloadIdentityUser"
  member  = "serviceAccount:${var.project_id}.svc.id.goog[isidro/db-client-microservice]"
}

resource "google_service_account" "kubebash_microservices" {
  account_id   = "isidro-kubebash-microservices"
  display_name = "Isidro Kubebash Microservices"
}

resource "google_project_iam_member" "kubebash_microservices_trace_writer" {
  project = var.project_id
  role    = "roles/cloudtrace.agent"
  member  = "serviceAccount:${google_service_account.kubebash_microservices.email}"
}

resource "google_project_iam_member" "kubebash_microservices_workload_identity_user" {
  project = var.project_id
  role    = "roles/iam.workloadIdentityUser"
  member  = "serviceAccount:${var.project_id}.svc.id.goog[isidro/kubebash-microservice]"
}