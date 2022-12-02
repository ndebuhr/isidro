resource "google_storage_bucket" "analytics" {
  name          = "isidro-analytics-${random_string.bucket_suffix.result}"
  location      = "US"
  force_destroy = true

  uniform_bucket_level_access = true
  public_access_prevention = "enforced"
}

resource "random_string" "bucket_suffix" {
  length = 8
  upper  = false
  special = false
}