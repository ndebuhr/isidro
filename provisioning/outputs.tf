output "client_token" {
  sensitive = true
  value     = base64encode(data.google_client_config.default.access_token)
}

output "binauthz_keyring" {
  value = google_kms_key_ring.isidro.name
}

output "binauthz_keyring_location" {
  value = google_kms_key_ring.isidro.location
}

output "binauthz_attestor" {
  value = google_binary_authorization_attestor.isidro.name
}

output "binauthz_key" {
  value = google_kms_crypto_key.isidro.name
}