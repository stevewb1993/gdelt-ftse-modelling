resource "google_service_account" "gdelt-service-account" {
  account_id   = "gdelt-service-account"
  display_name = "gdelt-service-account"
}

resource "google_service_account_key" "gdelt-service-account-key" {
  service_account_id = google_service_account.gdelt-service-account.name
}