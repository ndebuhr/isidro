resource "google_compute_network" "isidro" {
  name                    = var.network
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "primary" {
  name          = "primary"
  ip_cidr_range = var.primary_cluster_auxiliary_range
  region        = var.primary_cluster_region
  network       = google_compute_network.isidro.id
  secondary_ip_range {
    range_name    = "isidro-primary-pods"
    ip_cidr_range = var.primary_cluster_pods_range
  }
  secondary_ip_range {
    range_name    = "isidro-primary-services"
    ip_cidr_range = var.primary_cluster_services_range
  }
}

resource "google_compute_subnetwork" "secondary" {
  name          = "secondary"
  ip_cidr_range = var.secondary_cluster_auxiliary_range
  region        = var.secondary_cluster_region
  network       = google_compute_network.isidro.id
  secondary_ip_range {
    range_name    = "isidro-secondary-pods"
    ip_cidr_range = var.secondary_cluster_pods_range
  }
  secondary_ip_range {
    range_name    = "isidro-secondary-services"
    ip_cidr_range = var.secondary_cluster_services_range
  }
}

resource "google_compute_subnetwork" "config" {
  name          = "config"
  ip_cidr_range = var.config_cluster_auxiliary_range
  region        = var.config_cluster_region
  network       = google_compute_network.isidro.id
  secondary_ip_range {
    range_name    = "isidro-config-pods"
    ip_cidr_range = var.config_cluster_pods_range
  }
  secondary_ip_range {
    range_name    = "isidro-config-services"
    ip_cidr_range = var.config_cluster_services_range
  }
}