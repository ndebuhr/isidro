resource "google_service_account" "analytics" {
  account_id   = "isidro-analytics"
  display_name = "Isidro Analytics"
}

resource "google_project_iam_member" "analytics_dataflow_worker" {
  project = data.google_project.project.project_id
  role    = "roles/dataflow.worker"
  member  = "serviceAccount:${google_service_account.analytics.email}"
}

resource "google_project_iam_member" "analytics_dataflow_developer" {
  project = data.google_project.project.project_id
  role    = "roles/dataflow.developer"
  member  = "serviceAccount:${google_service_account.analytics.email}"
}

resource "google_project_iam_member" "analytics_storage_admin" {
  project = data.google_project.project.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.analytics.email}"
}

resource "google_project_iam_member" "analytics_bigquery_data_owner" {
  project = data.google_project.project.project_id
  role    = "roles/bigquery.dataOwner"
  member  = "serviceAccount:${google_service_account.analytics.email}"
}

resource "google_project_iam_member" "analytics_bigquery_job_user" {
  project = data.google_project.project.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.analytics.email}"
}

resource "google_project_iam_member" "analytics_sa_user" {
  project = data.google_project.project.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.analytics.email}"
}

resource "google_project_iam_member" "analytics_pubsub_editor" {
  project = data.google_project.project.project_id
  role    = "roles/pubsub.editor"
  member  = "serviceAccount:${google_service_account.analytics.email}"
}
