resource "google_artifact_registry_repository" "libs" {
  location      = "us"
  repository_id = "isidro-libs"
  description   = "Shared libraries for Isidro microservices"
  format        = "PYTHON"
}

resource "google_artifact_registry_repository_iam_member" "member" {
  project = google_artifact_registry_repository.libs.project
  location = google_artifact_registry_repository.libs.location
  repository = google_artifact_registry_repository.libs.name
  role = "roles/artifactregistry.reader"
  member = "allUsers"
}