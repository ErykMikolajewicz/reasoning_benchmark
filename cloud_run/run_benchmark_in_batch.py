import os

import google.auth
from googleapiclient.discovery import build
from google.auth import impersonated_credentials
from dotenv import load_dotenv

load_dotenv(".env")

SA_NAME = os.environ.get("SA_NAME")
PROJECT_ID = os.environ.get("PROJECT_ID")
LOCATION = os.environ.get("LOCATION")
JOB_NAME = "reasoning-benchmark-job"

IMAGE_NAME = "reasoning_benchmark"
IMAGE_TAG = "latest"
REGISTRY_HOST = f"{LOCATION}-docker.pkg.dev"
IMAGE = f"{REGISTRY_HOST}/{PROJECT_ID}/llm-benchmark-repository/{IMAGE_NAME}:{IMAGE_TAG}"

CPU_MILLI = 1000
MEM_MIB = "1024"

TIMEOUT_SECONDS = 8 * 60 * 60


CONTAINER_ENVS = [
    # {"name": "BENCHMARK_NAME", "value": "chess-tuned"},
    # {"name": "GCS_OUTPUT_BUCKET", "value": "gs://twoj-bucket"},
]

source_creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
target_creds = impersonated_credentials.Credentials(
    source_credentials=source_creds,
    target_principal=f"{SA_NAME}@{PROJECT_ID}.iam.gserviceaccount.com",
    target_scopes=["https://www.googleapis.com/auth/cloud-platform"],
    lifetime=3600,
)

batch = build("batch", "v1", credentials=target_creds, cache_discovery=False)

PARENT = f"projects/{PROJECT_ID}/locations/{LOCATION}"
JOB_FULL_NAME = f"{PARENT}/jobs/{JOB_NAME}"

# Ułóż env-y w formacie Batch
env_vars = {e["name"]: e["value"] for e in CONTAINER_ENVS} if CONTAINER_ENVS else {}

body = {
    "taskGroups": [
        {
            "taskSpec": {
                "runnables": [
                    {
                        "container": {
                            "imageUri": IMAGE
                        }
                    }
                ],
                "environment": {"variables": env_vars} if env_vars else {},
                "computeResource": {
                    "cpuMilli": CPU_MILLI,
                    "memoryMib": MEM_MIB
                },
                "maxRunDuration": f"{TIMEOUT_SECONDS}s"
            }
        }
    ],
    "allocationPolicy": {
        "instances": [
            {"policy": {"machineType": "g1-small"}}
        ],
        "serviceAccount": {
            "email": f"{SA_NAME}@{PROJECT_ID}.iam.gserviceaccount.com"
        }
    },
    "logsPolicy": {"destination": "CLOUD_LOGGING"},
    "labels": {"app": "llm-benchmark"}
}

batch.projects().locations().jobs().create(parent=PARENT, jobId=JOB_NAME, body=body).execute()
print(f"Created Batch job: {JOB_FULL_NAME}")

