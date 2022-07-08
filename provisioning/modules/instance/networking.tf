resource "google_compute_subnetwork" "instance" {
  name          = "config"
  ip_cidr_range = var.auxiliary_range
  region        = var.region
  network       = var.vpc
  secondary_ip_range {
    range_name    = "${var.name}-pods"
    ip_cidr_range = var.pods_range
  }
  secondary_ip_range {
    range_name    = "${var.name}-services"
    ip_cidr_range = var.services_range
  }
}