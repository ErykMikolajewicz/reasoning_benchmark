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
gcloud artifacts repositories create "llm-benchmark-repository" \
  --repository-format=docker \
  --location="$LOCATION"
gcloud artifacts repositories set-cleanup-policies "llm-benchmark-repository" \
  --location="$LOCATION" \
  --project="$PROJECT_ID" \
  --policy=policy.json \
  --no-dry-run

echo "Add to service account: $SA_NAME admin permissions on images repository: llm-benchmark-repository"
gcloud artifacts repositories add-iam-policy-binding "llm-benchmark-repository" \
  --location="$LOCATION" \
  --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"
#
#echo "Add service account $SA_NAME permissions to be executed by itself."
#gcloud iam service-accounts add-iam-policy-binding "$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
#  --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
#  --role="roles/iam.serviceAccountUser"

echo "Add to service account: $SA_NAME jobs permissions, and enable necessary apis."
# Enables apis, quite a lot, but it is written in documentation to do so:
# https://cloud.google.com/batch/docs/get-started#job-service-account
gcloud services enable \
  batch.googleapis.com \
  compute.googleapis.com \
  logging.googleapis.com
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/batch.jobsEditor"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/batch.agentReporter"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/logging.logWriter"

echo "Add desktop credentials for Python scripts"
gcloud auth application-default login
gcloud auth application-default set-quota-project "$PROJECT_ID"

echo "Enable api: IAM Service Account Credentials, and add permission to get token, for service account."
gcloud services enable iamcredentials.googleapis.com
gcloud iam service-accounts add-iam-policy-binding "$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --member="user:$CLOUD_USER_EMAIL" \
  --role="roles/iam.serviceAccountTokenCreator"

echo "Add to service account: $SA_NAME read only access to secrets in project $PROJECT_ID"
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

echo "Project configuration ended! Now you should manually add your api keys to secret manager in Google Cloud UI."
