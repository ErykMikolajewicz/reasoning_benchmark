#!/bin/bash
set -euo pipefail

if [[ ! -f .env ]]; then
  echo "File create_project.env not found. Create it from .env.example"
  exit 1
fi

source .env

echo "Creating project: ${PROJECT_ID} (llm-reasoning-benchmark)."
gcloud projects create "${PROJECT_ID}" --name="llm-reasoning-benchmark" --set-as-default

echo "Linking billing account: ${BILLING_ACCOUNT}"
gcloud billing projects link "${PROJECT_ID}" --billing-account="${BILLING_ACCOUNT}"

echo "Creating service to deploy benchmark."
gcloud iam service-accounts create "benchmark-deployer" --project="${PROJECT_ID}" --display-name="LLM chess benchmark deployer"

echo "Creating bucket: ${BUCKET_NAME} to store results."
gcloud storage buckets create "gs://${BUCKET_NAME}" --location="${LOCATION}" --uniform-bucket-level-access

echo "Add to service account: benchmark-runner admin permissions on objects in bucket: ${BUCKET_NAME}"
gcloud storage buckets add-iam-policy-binding "gs://${BUCKET_NAME}" \
    --member="serviceAccount:benchmark-runner@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/storage.objectAdmin"

echo "Creating repository: llm-benchmark-repository to store benchmark containers."
gcloud services enable artifactregistry.googleapis.com
gcloud artifacts repositories create "llm-benchmark-repository" \
  --repository-format=docker \
  --location="${LOCATION}"
gcloud artifacts repositories set-cleanup-policies "llm-benchmark-repository" \
  --location="${LOCATION}" \
  --project="${PROJECT_ID}" \
  --policy=policy.json \
  --no-dry-run

echo "Add to service account: benchmark-deployer admin permissions on images repository: llm-benchmark-repository"
gcloud artifacts repositories add-iam-policy-binding "llm-benchmark-repository" \
  --location="${LOCATION}" \
  --member="serviceAccount:benchmark-deployer@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

echo "Add service account benchmark-runner permissions to be executed by itself."
gcloud iam service-accounts add-iam-policy-binding "benchmark-runner@${PROJECT_ID}.iam.gserviceaccount.com" \
  --member="serviceAccount:benchmark-runner@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

echo "Add to service account: benchmark-runner jobs permissions, and enable necessary apis."
# Enables apis, quite a lot, but it is written in documentation to do so:
# https://cloud.google.com/batch/docs/get-started#job-service-account
gcloud services enable \
  batch.googleapis.com \
  compute.googleapis.com \
  logging.googleapis.com
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:benchmark-runner@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/batch.jobsEditor"

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:benchmark-runner@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/batch.agentReporter"

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:benchmark-runner@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/logging.logWriter"

echo "Add desktop credentials for Python scripts"
gcloud auth application-default login
gcloud auth application-default set-quota-project "${PROJECT_ID}"

echo "Enable api: IAM Service Account Credentials, and add permission to get token, for service accounts."
gcloud services enable iamcredentials.googleapis.com
gcloud iam service-accounts add-iam-policy-binding "benchmark-deployer@${PROJECT_ID}.iam.gserviceaccount.com" \
  --member="user:$CLOUD_USER_EMAIL" \
  --role="roles/iam.serviceAccountTokenCreator"
gcloud iam service-accounts add-iam-policy-binding "benchmark-runner@${PROJECT_ID}.iam.gserviceaccount.com" \
  --member="user:$CLOUD_USER_EMAIL" \
  --role="roles/iam.serviceAccountTokenCreator"

echo "Add to service account: benchmark-runner read only access to secrets in project ${PROJECT_ID},
 and enable secrets api"
gcloud services enable secretmanager.googleapis.com
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:benchmark-runner@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

echo "Project configuration ended! Now you should manually add your api keys to secret manager in Google Cloud UI.
on: https://console.cloud.google.com/security/secret-manager?project=${PROJECT_ID}"