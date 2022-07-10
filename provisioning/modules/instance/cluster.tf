data "google_project" "project" {}

module "gke" {
  source                      = "terraform-google-modules/kubernetes-engine/google//modules/beta-public-cluster"
  version                     = "21.2.0"
  project_id                  = data.google_project.project.project_id
  name                        = var.name
  regional                    = true
  region                      = var.region
  zones                       = var.zones
  release_channel             = "RAPID"
  network                     = var.vpc
  subnetwork                  = google_compute_subnetwork.instance.name
  ip_range_pods               = google_compute_subnetwork.instance.secondary_ip_range[0].range_name
  ip_range_services           = google_compute_subnetwork.instance.secondary_ip_range[1].range_name
  network_policy              = true
  create_service_account      = false
  service_account             = var.nodes_service_account
  enable_binary_authorization = true
  gce_pd_csi_driver           = true
  cluster_resource_labels     = { "mesh_id" : "proj-${data.google_project.project.number}" }
  node_pools = [
    {
      name         = "core"
      autoscaling  = var.autoscaling
      auto_upgrade = true
      node_count   = var.autoscaling ? 0 : var.node_count
      min_count    = var.autoscaling ? var.min_flex : 0
      max_count    = var.autoscaling ? var.max_flex : 0
      spot         = var.spot
      machine_type = var.machine_type
      enable_gcfs  = true
    }
  ]
  node_pools_oauth_scopes = {
    "all" : [
      "https://www.googleapis.com/auth/devstorage.read_only",
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
      "https://www.googleapis.com/auth/trace.append"
    ]
  }
}

module "asm" {
  source                    = "terraform-google-modules/kubernetes-engine/google//modules/asm"
  version                   = "21.2.0"
  cluster_name              = module.gke.name
  project_id                = data.google_project.project.project_id
  cluster_location          = module.gke.location
  enable_cni                = true
  enable_fleet_registration = true
  providers = {
    kubernetes = kubernetes
  }
}
