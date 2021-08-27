resource "google_project_service" "cloud-functions-api" {
  project = var.project_id
  service = "cloudfunctions.googleapis.com"
}

resource "google_project_service" "cloud-build-api" {
  project = var.project_id
  service = "cloudbuild.googleapis.com"
}

resource "google_project_service" "google-drive-api" {
  project = var.project_id
  service = "drive.googleapis.com"
}

resource "google_project_service" "google-sheets-api" {
  project = var.project_id
  service = "sheets.googleapis.com"
}

resource "google_project_service" "scheduler-api" {
  project = var.project_id
  service = "cloudscheduler.googleapis.com"
}

resource "google_project_service" "app-engine-api" {
  project = var.project_id
  service = "appengine.googleapis.com"
}


