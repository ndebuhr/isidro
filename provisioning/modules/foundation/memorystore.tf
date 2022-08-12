resource "google_redis_instance" "isidro" {
  name               = "isidro"
  tier               = "BASIC"
  memory_size_gb     = 8
  region             = "us-central1"
  authorized_network = google_compute_network.isidro.id
  display_name       = "isidro"
}
