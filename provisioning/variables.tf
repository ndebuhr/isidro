variable "network" {
  description = "The VPC network to create"
  default     = "isidro"
}

variable "primary_cluster_name" {
  description = "The name for the primary GKE cluster"
  default     = "isidro-us"
}

variable "primary_cluster_region" {
  description = "The primary cluster geographic region"
  default     = "us-central1"
}

variable "primary_cluster_pods_range" {
  description = "The secondary ip range to use for the primary cluster pods"
  default     = "172.16.64.0/19"
}

variable "primary_cluster_services_range" {
  description = "The secondary ip range to use for the primary cluster services"
  default     = "172.16.96.0/19"
}

variable "primary_cluster_auxiliary_range" {
  description = "The ip range for services outside the primary cluster, but in the primary cluster region"
  default     = "172.16.0.0/18"
}

variable "secondary_cluster_name" {
  description = "The name for the secondary GKE cluster"
  default     = "isidro-fi"
}

variable "secondary_cluster_region" {
  description = "The secondary cluster geographic region"
  default     = "europe-north1"
}

variable "secondary_cluster_pods_range" {
  description = "The secondary ip range to use for the secondary cluster pods"
  default     = "172.16.192.0/19"
}

variable "secondary_cluster_services_range" {
  description = "The secondary ip range to use for the secondary cluster services"
  default     = "172.16.224.0/19"
}

variable "secondary_cluster_auxiliary_range" {
  description = "The ip range for services outside the secondary cluster, but in the secondary cluster region"
  default     = "172.16.128.0/18"
}

variable "tertiary_cluster_name" {
  description = "The name for the tertiary GKE cluster"
  default     = "isidro-br"
}

variable "tertiary_cluster_region" {
  description = "The tertiary cluster geographic region"
  default     = "southamerica-east1"
}

variable "tertiary_cluster_pods_range" {
  description = "The tertiary ip range to use for the tertiary cluster pods"
  default     = "172.17.192.0/19"
}

variable "tertiary_cluster_services_range" {
  description = "The secondary ip range to use for the tertiary cluster services"
  default     = "172.17.224.0/19"
}

variable "tertiary_cluster_auxiliary_range" {
  description = "The ip range for services outside the tertiary cluster, but in the tertiary cluster region"
  default     = "172.17.128.0/18"
}

variable "config_cluster_name" {
  description = "The name for the config GKE cluster"
  default     = "isidro-config"
}

variable "config_cluster_region" {
  description = "The config cluster geographic region"
  default     = "northamerica-northeast1"
}

variable "config_cluster_pods_range" {
  description = "The secondary ip range to use for the config cluster pods"
  default     = "172.17.64.0/19"
}

variable "config_cluster_services_range" {
  description = "The secondary ip range to use for the config cluster services"
  default     = "172.17.96.0/19"
}

variable "config_cluster_auxiliary_range" {
  description = "The ip range for services outside the config cluster, but in the config cluster region"
  default     = "172.17.0.0/18"
}