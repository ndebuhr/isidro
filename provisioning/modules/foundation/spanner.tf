resource "google_spanner_instance" "isidro" {
  config           = var.spanner_config
  name             = "isidro"
  display_name     = "isidro"
  processing_units = 100
}

resource "google_spanner_database" "isidro" {
  instance = google_spanner_instance.isidro.name
  name     = "isidro"
  ddl = [
    <<EOT
    CREATE TABLE posts (
      id STRING(255) NOT NULL,
      updated_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true),
      channel STRING(255) NOT NULL,
      thread_ts STRING(255) NOT NULL,
      user STRING(255) NOT NULL,
      text STRING(8191) NOT NULL
    )
    PRIMARY KEY(id)
    EOT
  ]
  deletion_protection = false
}