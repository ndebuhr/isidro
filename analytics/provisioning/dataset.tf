resource "google_bigquery_dataset" "gtm_stream" {
  dataset_id                  = "isidro_gtm_stream"
  friendly_name               = "Isidro GTM Stream"
  description                 = "Datasets around the Google Tag Manager stream for Isidro"
  location                    = "US"
}