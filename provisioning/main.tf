data "google_client_config" "default" {}

provider "kubernetes" {
  host                   = "https://${module.gke.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(module.gke.ca_certificate)
}

data "google_project" "project" {}

module "gke" {
  source                      = "github.com/terraform-google-modules/terraform-google-kubernetes-engine"
  project_id                  = data.google_project.project.project_id
  name                        = var.cluster_name
  regional                    = true
  region                      = var.region
  release_channel             = "REGULAR"
  network                     = var.network
  subnetwork                  = var.subnetwork
  ip_range_pods               = var.ip_range_pods
  ip_range_services           = var.ip_range_services
  network_policy              = true
  create_service_account      = false
  service_account             = google_service_account.isidro_nodes.email
  enable_binary_authorization = true
  cluster_resource_labels     = { "mesh_id" : "proj-${data.google_project.project.number}" }
  node_pools = [
    {
      name         = "asm-node-pool"
      autoscaling  = false
      auto_upgrade = true
      # ASM requires minimum 4 nodes and e2-standard-4
      node_count   = 1
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

module "asm" {
  source                    = "github.com/terraform-google-modules/terraform-google-kubernetes-engine//modules/asm"
  cluster_name              = module.gke.name
  project_id                = data.google_project.project.project_id
  cluster_location          = module.gke.location
  enable_cni                = true
  enable_fleet_registration = true
  enable_mesh_feature       = false
  fleet_id                  = "isidro"
}
