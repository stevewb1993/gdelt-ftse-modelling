provider "google" {
  project   = var.project_id
  region    = var.region
  zone      = "europe-west2-a"
}

# resource "google_cloudfunctions_function" "function" {
#   name        = "function-test"
#   description = "My function"
#   runtime     = "python39"
# 
#   available_memory_mb   = 128
#   trigger_http          = true
#   timeout               = 60
#   
# }