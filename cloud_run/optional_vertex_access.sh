#!/bin/bash
set -euo pipefail

if [[ ! -f .env ]]; then
  echo "File create_project.env not found. Create it from .env.example"
  exit 1
fi

source .env

echo "Enabling AI api in Google Cloud."
gcloud services enable aiplatform.googleapis.com iamcredentials.googleapis.com --project "${PROJECT_ID}"

echo "Add privileges to use models in Vertex"
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:benchmark-runner@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

echo "Now enable model in Google Clou GUI, for example for llama3:
https://console.cloud.google.com/vertex-ai/publishers/meta/model-garden/llama-3.3-70b-instruct-maas?project=${PROJECT_ID}"
