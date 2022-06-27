provider "kubernetes" {
  alias                  = "tertiary"
  host                   = "https://${module.gke_tertiary.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(module.gke_tertiary.ca_certificate)
}

module "gke_tertiary" {
  depends_on = [
    google_compute_subnetwork.tertiary
  ]
  source                      = "terraform-google-modules/kubernetes-engine/google//modules/beta-public-cluster"
  version                     = "21.2.0"
  project_id                  = data.google_project.project.project_id
  name                        = var.tertiary_cluster_name
  regional                    = true
  region                      = var.tertiary_cluster_region
  release_channel             = "RAPID"
  network                     = var.network
  subnetwork                  = google_compute_subnetwork.tertiary.name
  ip_range_pods               = "isidro-tertiary-pods"
  ip_range_services           = "isidro-tertiary-services"
  network_policy              = true
  create_service_account      = false
  service_account             = google_service_account.nodes.email
  enable_binary_authorization = true
  gce_pd_csi_driver           = true
  cluster_resource_labels     = { "mesh_id" : "proj-${data.google_project.project.number}" }
  node_pools = [
    {
      name         = "spot-nodes"
      autoscaling  = false
      auto_upgrade = true
      node_count   = 1
      spot         = true
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

module "asm_tertiary" {
  source                    = "github.com/terraform-google-modules/terraform-google-kubernetes-engine//modules/asm"
  cluster_name              = module.gke_tertiary.name
  project_id                = data.google_project.project.project_id
  cluster_location          = module.gke_tertiary.location
  enable_cni                = true
  enable_fleet_registration = true
  providers = {
    kubernetes = kubernetes.tertiary
  }
}