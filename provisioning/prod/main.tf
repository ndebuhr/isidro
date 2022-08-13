data "google_project" "project" {}
data "google_client_config" "default" {}

module "foundations" {
  source           = "../modules/foundation"
  project_number   = data.google_project.project.number
  project_id       = data.google_project.project.project_id
  spanner_config   = "nam-eur-asia3"
  memorystore_tier = "STANDARD_HA"
  gbash_role       = "roles/editor"
}

module "primary" {
  source                 = "../modules/instance"
  name                   = "isidro-us-ia"
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

module "secondary" {
  source                 = "../modules/instance"
  name                   = "isidro-us-sc"
  vpc                    = module.foundations.vpc_name
  auxiliary_range        = "172.16.128.0/18"
  pods_range             = "172.16.192.0/19"
  services_range         = "172.16.224.0/19"
  region                 = "us-east1"
  zones                  = ["us-east1-c", "us-east1-d"]
  node_count             = 1
  nodes_service_account  = module.foundations.nodes_sa_email
  spot                   = true
  machine_type           = "t2d-standard-4"
  binauthz_attestor_name = module.foundations.binauthz_attestor
  providers = {
    kubernetes = kubernetes.secondary
  }
}

provider "kubernetes" {
  alias                  = "secondary"
  host                   = "https://${module.secondary.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(module.secondary.ca_certificate)
}

module "tertiary" {
  source                 = "../modules/instance"
  name                   = "isidro-be"
  vpc                    = module.foundations.vpc_name
  auxiliary_range        = "172.17.0.0/18"
  pods_range             = "172.17.64.0/19"
  services_range         = "172.17.96.0/19"
  region                 = "europe-west1"
  zones                  = ["europe-west1-b", "europe-west1-d"]
  node_count             = 1
  nodes_service_account  = module.foundations.nodes_sa_email
  spot                   = true
  machine_type           = "t2d-standard-4"
  binauthz_attestor_name = module.foundations.binauthz_attestor
  providers = {
    kubernetes = kubernetes.tertiary
  }
}

provider "kubernetes" {
  alias                  = "tertiary"
  host                   = "https://${module.tertiary.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(module.tertiary.ca_certificate)
}

module "quaternary" {
  source                 = "../modules/instance"
  name                   = "isidro-nl"
  vpc                    = module.foundations.vpc_name
  auxiliary_range        = "172.17.128.0/18"
  pods_range             = "172.17.192.0/19"
  services_range         = "172.17.224.0/19"
  region                 = "europe-west4"
  zones                  = ["europe-west4-a", "europe-west4-b"]
  node_count             = 1
  nodes_service_account  = module.foundations.nodes_sa_email
  spot                   = true
  machine_type           = "t2d-standard-4"
  binauthz_attestor_name = module.foundations.binauthz_attestor
  providers = {
    kubernetes = kubernetes.quaternary
  }
}

provider "kubernetes" {
  alias                  = "quaternary"
  host                   = "https://${module.quaternary.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(module.quaternary.ca_certificate)
}

module "quinary" {
  source                 = "../modules/instance"
  name                   = "isidro-tw"
  vpc                    = module.foundations.vpc_name
  auxiliary_range        = "172.18.0.0/18"
  pods_range             = "172.18.64.0/19"
  services_range         = "172.18.96.0/19"
  region                 = "asia-east1"
  zones                  = ["asia-east1-a", "asia-east1-b"]
  node_count             = 1
  nodes_service_account  = module.foundations.nodes_sa_email
  spot                   = true
  machine_type           = "t2d-standard-4"
  binauthz_attestor_name = module.foundations.binauthz_attestor
  providers = {
    kubernetes = kubernetes.quinary
  }
}

provider "kubernetes" {
  alias                  = "quinary"
  host                   = "https://${module.quinary.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(module.quinary.ca_certificate)
}

module "config" {
  source                 = "../modules/instance"
  name                   = "isidro-config"
  vpc                    = module.foundations.vpc_name
  auxiliary_range        = "172.18.128.0/18"
  pods_range             = "172.18.192.0/19"
  services_range         = "172.18.224.0/19"
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