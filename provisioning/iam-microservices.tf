resource "google_service_account" "tracing_microservices" {
  account_id   = "isidro-tracing-microservices"
  display_name = "Isidro Tracing Microservices"
}

resource "google_project_iam_member" "tracing_microservices_trace_writer" {
  project = data.google_project.project.project_id
  role    = "roles/cloudtrace.agent"
  member  = "serviceAccount:${google_service_account.tracing_microservices.email}"
}

resource "google_project_iam_member" "tracing_microservices_workload_identity_user" {
  project = data.google_project.project.project_id
  role    = "roles/iam.workloadIdentityUser"
  member  = "serviceAccount:${data.google_project.project.project_id}.svc.id.goog[isidro/tracing-microservice]"
}

