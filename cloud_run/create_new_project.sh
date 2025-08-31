#!/bin/bash
set -euo pipefail

if [[ ! -f .env ]]; then
  echo "File create_project.env not found. Create it from .env.example"
  exit 1
fi

source .env

echo "Creating project: $PROJECT_ID (llm-reasoning-benchmark)."
gcloud projects create "$PROJECT_ID" --name="llm-reasoning-benchmark" --set-as-default

echo "Linking billing account: $BILLING_ACCOUNT"
gcloud billing projects link "$PROJECT_ID" --billing-account="$BILLING_ACCOUNT"

echo "Creating service account to launch benchmark."
gcloud iam service-accounts create "$SA_NAME" --project="$PROJECT_ID" --display-name="LLM chess benchmark runner"

echo "Creating bucket: $BUCKET_NAME to store results."
gcloud storage buckets create "gs://$BUCKET_NAME" --location="$LOCATION" --uniform-bucket-level-access

echo "Make bucket $BUCKET_NAME publicly accessible to read."
gcloud storage buckets add-iam-policy-binding "gs://$BUCKET_NAME" \
    --member="allUsers" \
    --role="roles/storage.objectViewer"

echo "Add to service account: $SA_NAME admin permissions on objects in bucket: $BUCKET_NAME"
gcloud storage buckets add-iam-policy-binding "gs://$BUCKET_NAME" \
    --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

echo "Creating repository: llm-benchmark-repository to store benchmark containers."
gcloud services enable artifactregistry.googleapis.com
gcloud artifacts repositories create "llm-benchmark-repository" --repository-format=docker --location="$LOCATION"

echo "Add to service account: $SA_NAME admin permissions on images repository: llm-benchmark-repository"
gcloud artifacts repositories add-iam-policy-binding "llm-benchmark-repository" \
  --location="$LOCATION" \
  --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.repoAdmin"

echo "Add to service account: $SA_NAME admin permissions for running images in Cloud Run"
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

echo "Add to service account: $SA_NAME read only access to secrets in project $PROJECT_ID"
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

echo "Add desktop credentials for Python scripts"
gcloud auth application-default login
gcloud auth application-default set-quota-project "$PROJECT_ID"

gcloud services enable iamcredentials.googleapis.com run.googleapis.com
gcloud iam service-accounts add-iam-policy-binding "$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --member="user:$CLOUD_USER_EMAIL" \
  --role="roles/iam.serviceAccountTokenCreator"

echo "Project configuration ended! Now you should manually add your api keys to secret manager in Google Cloud UI."
