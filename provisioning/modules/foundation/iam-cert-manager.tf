resource "google_service_account" "cert_manager" {
  account_id   = "isidro-cert-manager"
  display_name = "Isidro Cert Manager"
}

resource "google_project_iam_member" "cert_manager_dns_admin" {
  project = var.project_id
  role    = "roles/dns.admin"
  member  = "serviceAccount:${google_service_account.cert_manager.email}"
}

resource "google_project_iam_member" "cert_manager_workload_identity_user" {
  project = var.project_id
  role    = "roles/iam.workloadIdentityUser"
  member  = "serviceAccount:${var.project_id}.svc.id.goog[cert-manager/cert-manager]"
}

