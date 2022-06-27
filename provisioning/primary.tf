provider "kubernetes" {
  alias                  = "primary"
  host                   = "https://${module.gke_primary.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(module.gke_primary.ca_certificate)
}

module "gke_primary" {
  depends_on = [
    google_compute_subnetwork.primary
  ]
  source                      = "terraform-google-modules/kubernetes-engine/google//modules/beta-public-cluster"
  version                     = "21.2.0"
  project_id                  = data.google_project.project.project_id
  name                        = var.primary_cluster_name
  regional                    = true
  region                      = var.primary_cluster_region
  release_channel             = "RAPID"
  network                     = var.network
  subnetwork                  = google_compute_subnetwork.primary.name
  ip_range_pods               = "isidro-primary-pods"
  ip_range_services           = "isidro-primary-services"
  network_policy              = true
  create_service_account      = false
  service_account             = google_service_account.nodes.email
  enable_binary_authorization = true
  gce_pd_csi_driver           = true
  cluster_resource_labels     = { "mesh_id" : "proj-${data.google_project.project.number}" }
  node_pools = [
    {
      name         = "core-nodes"
      autoscaling  = false
      auto_upgrade = true
      node_count   = 1
      machine_type = "t2d-standard-2"
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

module "asm_primary" {
  source                    = "github.com/terraform-google-modules/terraform-google-kubernetes-engine//modules/asm"
  cluster_name              = module.gke_primary.name
  project_id                = data.google_project.project.project_id
  cluster_location          = module.gke_primary.location
  enable_cni                = true
  enable_fleet_registration = true
  providers = {
    kubernetes = kubernetes.primary
  }
}