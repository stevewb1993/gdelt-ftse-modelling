
resource "google_storage_bucket" "model-storage" {
  name    = "gdelt-ftse-model-storage"
  location = "EU"
  force_destroy = true

}

resource "google_project_service" "ai-platform-api" {
  project = var.project_id
  service = "ml.googleapis.com"
}


resource "google_ml_engine_model" "gdelt_ftse_regression_model" {
  name        = "gdelt_ftse_regression_model"
  regions     = ["europe-west1"]
}

resource "google_storage_bucket_object" "ml-model-file" {
  name   = "model.joblib"
  bucket = google_storage_bucket.model-storage.name
  source = "../model_generation/model.joblib"
}
