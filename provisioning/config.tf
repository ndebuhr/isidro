data "google_client_config" "default" {}
data "google_project" "project" {}

provider "kubernetes" {
  alias                  = "config"
  host                   = "https://${module.gke_config.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(module.gke_config.ca_certificate)
}

module "gke_config" {
  source                      = "github.com/terraform-google-modules/terraform-google-kubernetes-engine//modules/beta-autopilot-public-cluster"
  project_id                  = data.google_project.project.project_id
  name                        = var.cluster_name_config
  regional                    = true
  region                      = var.region_config
  release_channel             = "REGULAR"
  network                     = var.network
  subnetwork                  = var.subnetwork_config
  ip_range_pods               = var.ip_range_pods_config
  ip_range_services           = var.ip_range_services_config
  enable_vertical_pod_autoscaling = true
  cluster_resource_labels     = { "mesh_id" : "proj-${data.google_project.project.number}" }
}

module "asm_config" {
  source                    = "github.com/terraform-google-modules/terraform-google-kubernetes-engine//modules/asm"
  cluster_name              = module.gke_config.name
  project_id                = data.google_project.project.project_id
  cluster_location          = module.gke_config.location
  enable_cni                = true
  enable_fleet_registration = true
  providers = {
    kubernetes = kubernetes.config
  }
}

resource "google_gke_hub_feature" "mci" {
  depends_on = [
    module.asm_config
  ]
  name = "multiclusteringress"
  location = "global"
  spec {
    multiclusteringress {
      config_membership = "projects/${data.google_project.project.project_id}/locations/global/memberships/${var.cluster_name_config}-membership"
    }
  }
  provider = google-beta
}

resource "google_compute_global_address" "isidro" {
  name = "isidro"
}