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
  --location="$LOCATION" \
  --cleanup-policy="policy=KEEP,condition=keepCount=1"

echo "Add to service account: $SA_NAME admin permissions on images repository: llm-benchmark-repository"
gcloud artifacts repositories add-iam-policy-binding "llm-benchmark-repository" \
  --location="$LOCATION" \
  --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

#echo "Add service account $SA_NAME permissions to be executed by itself."
#gcloud iam service-accounts add-iam-policy-binding "$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
#  --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
#  --role="roles/iam.serviceAccountUser"

echo "Add to service account: $SA_NAME jobs editor permissions, to launch container as batch job."
gcloud services enable batch.googleapis.com
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/batch.jobsEditor"

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


gcloud projects add-iam-policy-binding "llm-reasoning-benchmark" \
  --member="serviceAccount:benchmark-runner@llm-reasoning-benchmark.iam.gserviceaccount.com" \
  --role="roles/batch.jobsEditor"
