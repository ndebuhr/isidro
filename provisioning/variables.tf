variable "network" {
  description = "The VPC network to host the cluster in"
  default     = "default"
}

variable "cluster_name_primary" {
  description = "The name for the GKE cluster name"
  default     = "isidro-us"
}

variable "region_primary" {
  description = "The first region to host the cluster in"
  default     = "us-central1"
}

variable "subnetwork_primary" {
  description = "The region one subnetwork to host the cluster in"
  default     = "default"
}

variable "ip_range_pods_primary" {
  description = "The region one secondary ip range to use for pods"
}

variable "ip_range_services_primary" {
  description = "The region one secondary ip range to use for services"
}

variable "cluster_name_secondary" {
  description = "The name for the GKE cluster name"
  default     = "isidro-europe"
}

variable "region_secondary" {
  description = "The second region to host the cluster in"
  default     = "europe-west1"
}

variable "subnetwork_secondary" {
  description = "The region two subnetwork to host the cluster in"
  default     = "default"
}

variable "ip_range_pods_secondary" {
  description = "The region two secondary ip range to use for pods"
}

variable "ip_range_services_secondary" {
  description = "The region two secondary ip range to use for services"
}

variable "cluster_name_config" {
  description = "The name for the GKE cluster name"
  default     = "isidro-config"
}

variable "region_config" {
  description = "The region to host the config cluster in"
  default     = "northamerica-northeast1"
}

variable "subnetwork_config" {
  description = "The config cluster region subnetwork"
  default     = "default"
}

variable "ip_range_pods_config" {
  description = "The config cluster region secondary ip range to use for pods"
}

variable "ip_range_services_config" {
  description = "The config cluster region secondary ip range to use for services"
}