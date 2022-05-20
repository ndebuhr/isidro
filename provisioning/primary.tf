provider "kubernetes" {
  alias                  = "primary"
  host                   = "https://${module.gke_primary.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(module.gke_primary.ca_certificate)
}

module "gke_primary" {
  source                      = "github.com/terraform-google-modules/terraform-google-kubernetes-engine//modules/beta-public-cluster"
  project_id                  = data.google_project.project.project_id
  name                        = var.cluster_name_primary
  regional                    = true
  region                      = var.region_primary
  release_channel             = "REGULAR"
  network                     = var.network
  subnetwork                  = var.subnetwork_primary
  ip_range_pods               = var.ip_range_pods_primary
  ip_range_services           = var.ip_range_services_primary
  network_policy              = true
  create_service_account      = false
  service_account             = google_service_account.nodes.email
  enable_binary_authorization = true
  gce_pd_csi_driver           = true
  cluster_resource_labels     = { "mesh_id" : "proj-${data.google_project.project.number}" }
  node_pools = [
    {
      name         = "asm-node-pool"
      autoscaling  = false
      auto_upgrade = true
      # ASM requires minimum 4 nodes and e2-standard-4
      node_count   = 1
      spot         = true
      machine_type = "e2-standard-4"
    },
  ]
  node_pools_oauth_scopes = {
    # TODO: This seems to have no effect, or is overwritten by cloud_platform
    "asm-node-pool" : [
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