data "google_client_config" "default" {}
data "google_project" "project" {}

provider "kubernetes" {
  alias                  = "config"
  host                   = "https://${module.gke_config.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(module.gke_config.ca_certificate)
}

module "gke_config" {
  depends_on = [
    google_compute_subnetwork.config
  ]
  source                          = "terraform-google-modules/kubernetes-engine/google//modules/beta-autopilot-public-cluster"
  version                         = "21.2.0"
  project_id                      = data.google_project.project.project_id
  name                            = var.config_cluster_name
  regional                        = true
  region                          = var.config_cluster_region
  release_channel                 = "RAPID"
  network                         = var.network
  subnetwork                      = google_compute_subnetwork.config.name
  ip_range_pods                   = "isidro-config-pods"
  ip_range_services               = "isidro-config-services"
  enable_vertical_pod_autoscaling = true
  cluster_resource_labels         = { "mesh_id" : "proj-${data.google_project.project.number}" }
}

module "asm_config" {
  source                    = "terraform-google-modules/kubernetes-engine/google//modules/asm"
  version                   = "21.2.0"
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
  name     = "multiclusteringress"
  location = "global"
  spec {
    multiclusteringress {
      config_membership = "projects/${data.google_project.project.project_id}/locations/global/memberships/${var.config_cluster_name}-membership"
    }
  }
  provider = google-beta
}