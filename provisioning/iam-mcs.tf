resource "google_project_iam_member" "mcs_network_viewer" {
  project = data.google_project.project.project_id
  role    = "roles/compute.networkViewer"
  member  = "serviceAccount:${data.google_project.project.project_id}.svc.id.goog[gke-mcs/gke-mcs-importer]"
}