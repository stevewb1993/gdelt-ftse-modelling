# resource "google_app_engine_application" "app" {
#   project     = var.project_id
#   location_id = var.region
# }

resource "google_cloud_scheduler_job" "job" {
  name        = "test-job"
  description = "test job"
  schedule    = "0 23 * * *"


  http_target {
    http_method = "POST"
    uri         = "https://europe-west2-gdelt-ftse.cloudfunctions.net/ftse-predictor"
    body        = base64encode("{\"foo\":\"bar\"}")
  }
}