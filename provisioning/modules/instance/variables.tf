variable "name" {
  description = "Name of the GKE cluster"
}

variable "vpc" {
  description = "Name of the existing VPC"
}

variable "auxiliary_range" {
  description = "CIDR range for non-GKE resources"
}

variable "pods_range" {
  description = "CIDR range for GKE pods"
}

variable "services_range" {
  description = "CIDR range for GKE services"
}

variable "region" {
  description = "GKE region"
}

variable "zones" {
  description = "GKE zones"
}

variable "node_count" {
  description = "Count of GKE nodes (per zone), if autoscaling and NAP are not used"
  default     = 1
}

variable "autoprovisioning" {
  description = "Enable GKE node autoprovisioning"
  default     = false
}

variable "autoscaling" {
  description = "Enable GKE node autoscaling"
  default     = false
}

variable "min_flex" {
  description = "Minimum number of GKE nodes, if node autoscaling is used"
  default     = 1
}

variable "max_flex" {
  description = "Maximum number of GKE nodes, if node autoscaling is used"
  default     = 1
}

variable "nodes_service_account" {
  description = "Service account for GKE nodes"
}

variable "spot" {
  description = "Use spot instances"
}

variable "machine_type" {
  description = "Machine type for GKE nodes"
}

variable "binauthz_attestor_name" {
  description = "Binary authorization attestor name"
}