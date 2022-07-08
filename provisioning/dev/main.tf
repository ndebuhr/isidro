data "google_project" "project" {}
data "google_client_config" "default" {}

module "foundations" {
  source = "../modules/foundation"
  project_number = data.google_project.project.number
  project_id = data.google_project.project.project_id

}

module "primary" {
  source                 = "../modules/instance"
  name                   = "isidro-us"
  vpc                    = module.foundations.vpc_name
  auxiliary_range        = "172.16.0.0/18"
  pods_range             = "172.16.64.0/19"
  services_range         = "172.16.96.0/19"
  region                 = "us-central1"
  zones                  = ["us-central1-a", "us-central1-c", "us-central1-f"]
  node_count             = 1
  nodes_service_account  = module.foundations.nodes_sa_email
  spot                   = false
  machine_type           = "t2d-standard-4"
  binauthz_attestor_name = module.foundations.binauthz_attestor
  providers = {
    kubernetes = kubernetes.primary
  }
}

provider "kubernetes" {
  alias                  = "primary"
  host                   = "https://${module.primary.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(module.primary.ca_certificate)
}

module "config" {
  source                 = "../modules/instance"
  name                   = "isidro-config"
  vpc                    = module.foundations.vpc_name
  auxiliary_range        = "172.17.0.0/18"
  pods_range             = "172.17.64.0/19"
  services_range         = "172.17.96.0/19"
  region                 = "northamerica-northeast1"
  zones                  = ["northamerica-northeast1-b", "northamerica-northeast1-c"]
  node_count             = 1
  nodes_service_account  = module.foundations.nodes_sa_email
  spot                   = false
  machine_type           = "e2-standard-2"
  binauthz_attestor_name = module.foundations.binauthz_attestor
  providers = {
    kubernetes = kubernetes.config
  }
}

provider "kubernetes" {
  alias                  = "config"
  host                   = "https://${module.config.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(module.config.ca_certificate)
}

resource "google_gke_hub_feature" "mci" {
  depends_on = [
    module.config
  ]
  name     = "multiclusteringress"
  location = "global"
  spec {
    multiclusteringress {
      config_membership = "projects/${data.google_project.project.project_id}/locations/global/memberships/${module.config.name}-membership"
    }
  }
  provider = google-beta
}