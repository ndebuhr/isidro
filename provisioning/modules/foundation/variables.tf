variable "project_id" {
  description = "The project ID where resources will be deployed to"
}

variable "project_number" {
  description = "The project number where resources will be deployed to"
}

variable "spanner_config" {
  description = "The geographic config for the Isidro operational database"
}

variable "memorystore_tier" {
  description = "The Cloud Memorystore (Redis) tier, for the instance that will be used to back asynchronous task queues"
}

variable "memorystore_size" {
  description = "The Cloud Memorystore (Redis) GB size, for the instance that will be used to back asynchronous task queues"
}

variable "gbash_role" {
  description = "GCP IAM role to attach to the gBash service, which enables gcloud CLI commands within chatbot workflows"
}