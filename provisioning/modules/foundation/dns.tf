resource "google_dns_managed_zone" "isidro_local" {
  name        = "isidro-local"
  dns_name    = "isidro.local."
  description = "Private DNS zone for Isidro"

  visibility = "private"

  private_visibility_config {
    networks {
      network_url = google_compute_network.isidro.id
    }
  }
}

resource "google_dns_record_set" "redis" {
  name = "redis.${google_dns_managed_zone.isidro_local.dns_name}"
  type = "A"
  ttl  = 300

  managed_zone = google_dns_managed_zone.isidro_local.name

  rrdatas = [google_redis_instance.isidro.host]
}