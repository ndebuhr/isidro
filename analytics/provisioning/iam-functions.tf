resource "google_service_account" "analytics_functions" {
  account_id   = "isidro-analytics-functions"
  display_name = "Isidro Analytics Functions"
}

resource "google_project_iam_member" "analytics_functions_dns_admin" {
  project = data.google_project.project.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.analytics_functions.email}"
}
