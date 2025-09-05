import os
import subprocess

import google.auth
from google.auth import impersonated_credentials
from google.auth.transport.requests import Request

from dotenv import load_dotenv

load_dotenv(".env")

SA_NAME = os.environ.get("SA_NAME")
PROJECT_ID = os.environ.get("PROJECT_ID")
LOCATION = os.environ.get("LOCATION")

source_creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
target_creds = impersonated_credentials.Credentials(
    source_credentials=source_creds,
    target_principal=f"{SA_NAME}@{PROJECT_ID}.iam.gserviceaccount.com",
    target_scopes=["https://www.googleapis.com/auth/cloud-platform"],
    lifetime=3600,
)

target_creds.refresh(Request())
token = target_creds.token

registry_host = f"{LOCATION}-docker.pkg.dev"

image_name, tag = "reasoning_benchmark", "latest"

remote_ref = f"{registry_host}/{PROJECT_ID}/llm-benchmark-repository/{image_name}:{tag}"


login = subprocess.Popen(
    ["podman", "login", "-u", "oauth2accesstoken", "--password-stdin", f"https://{registry_host}"],
    stdin=subprocess.PIPE,
)
stdout, stderr = login.communicate(input=token.encode("utf-8"))
if login.returncode != 0:
    raise RuntimeError("podman login nie powiódł się")

subprocess.run(["podman", "tag", "reasoning_benchmark:latest", remote_ref])
subprocess.run(["podman", "push", remote_ref])

print(f"Sukces! Wypchnięto obraz: {remote_ref}")
