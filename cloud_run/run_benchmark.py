import os

import google.auth

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth import impersonated_credentials
from dotenv import load_dotenv

load_dotenv(".env")

SA_NAME = os.environ.get("SA_NAME")
PROJECT_ID = os.environ.get("PROJECT_ID")
LOCATION = os.environ.get("LOCATION")
SERVICE_NAME = os.environ.get("SERVICE_NAME", "reasoning-benchmark-svc")

IMAGE_NAME = "reasoning_benchmark"
IMAGE_TAG = "latest"
REGISTRY_HOST = f"{LOCATION}-docker.pkg.dev"
IMAGE = f"{REGISTRY_HOST}/{PROJECT_ID}/llm-benchmark-repository/{IMAGE_NAME}:{IMAGE_TAG}"

CPU = "1"
MEM = "512Mi"

source_creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
target_creds = impersonated_credentials.Credentials(
    source_credentials=source_creds,
    target_principal=f"{SA_NAME}@{PROJECT_ID}.iam.gserviceaccount.com",
    target_scopes=["https://www.googleapis.com/auth/cloud-platform"],
    lifetime=3600,
)

JOB_NAME = SERVICE_NAME
PARENT = f"projects/{PROJECT_ID}/locations/{LOCATION}"
JOB_FULL_NAME = f"{PARENT}/jobs/{JOB_NAME}"

TASK_COUNT = 1
PARALLELISM = 1
TIMEOUT_SECONDS = 3600
MAX_RETRIES = 0

CONTAINER_ENVS = [
    # {"name": "BENCHMARK_NAME", "value": "chess-tuned"},
    # {"name": "GCS_OUTPUT_BUCKET", "value": "gs://twoj-bucket"},
]


crun = build("run", "v2", credentials=target_creds, cache_discovery=False)

body = {
    "template": {
        "taskCount": TASK_COUNT,
        "parallelism": PARALLELISM,
        "template": {
            "serviceAccount": f"{SA_NAME}@{PROJECT_ID}.iam.gserviceaccount.com",
            "maxRetries": MAX_RETRIES,
            "timeout": f"{TIMEOUT_SECONDS}s",
            "executionEnvironment": "EXECUTION_ENVIRONMENT_GEN2",
            "containers": [{
                "image": IMAGE,
                "env": CONTAINER_ENVS,
                "resources": {"limits": {"cpu": CPU, "memory": MEM}},
            }],
        },
    },
}

try:
    crun.projects().locations().jobs().create(
        parent=PARENT, jobId=JOB_NAME, body=body
    ).execute()
    print(f"[OK] Utworzono job: {JOB_FULL_NAME}")
except HttpError as e:
    if e.resp.status == 409:
        crun.projects().locations().jobs().patch(
            name=JOB_FULL_NAME, body=body
        ).execute()
        print(f"[OK] Zaktualizowano istniejący job: {JOB_FULL_NAME}")
    else:
        raise

resp = crun.projects().locations().jobs().run(name=JOB_FULL_NAME, body={}).execute()
execution_name = resp.get("name", "<unknown>")
print(f"[STARTED] Execution: {execution_name}")
