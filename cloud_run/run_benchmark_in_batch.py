import os
from pathlib import Path

import google.auth
from googleapiclient.discovery import build
from google.auth import impersonated_credentials
from dotenv import load_dotenv, dotenv_values

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

ENVS_FILE_PATHS = ['application.env', 'benchmark.env', 'engine.env', 'analyze.env']
SETTINGS_PATH = Path('../settings')
container_envs = {}
for envs_file_path in ENVS_FILE_PATHS:
    envs_file_path = SETTINGS_PATH / envs_file_path
    file_env = dotenv_values(envs_file_path)
    container_envs.update(file_env)


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
                "environment": {"variables": container_envs},
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
