import os
from pathlib import Path
from uuid import uuid4

import google.auth
from dotenv import dotenv_values, load_dotenv
from google.auth import impersonated_credentials
from google.cloud import batch_v1

load_dotenv()

PROJECT_ID = os.environ["PROJECT_ID"]
LOCATION = os.environ["LOCATION"]
JOB_NAME = f"reasoning-benchmark-{str(uuid4())}"
VIRTUAL_MACHINE = "e2-small"

IMAGE_NAME, IMAGE_TAG = "reasoning_benchmark", "latest"
REGISTRY_HOST = f"{LOCATION}-docker.pkg.dev"
IMAGE_URI = f"{REGISTRY_HOST}/{PROJECT_ID}/llm-benchmark-repository/{IMAGE_NAME}:{IMAGE_TAG}"
SERVICE_EMAIL = f"benchmark-runner@{PROJECT_ID}.iam.gserviceaccount.com"

CPU_MILLI = 2000
MEM_MIB = 2000
MAX_DURATION = str(8 * 60 * 60) + 's'

ENVS_FILE_PATHS = ["application.env", "benchmark.env", "engine.env", "analyze.env"]
SETTINGS_PATH = Path("../settings")
container_envs = {}
for envs_file_path in ENVS_FILE_PATHS:
    envs_file_path = SETTINGS_PATH / envs_file_path
    file_env = dotenv_values(envs_file_path)
    container_envs.update(file_env)

secret_envs_names = list(dotenv_values(SETTINGS_PATH / "api_keys.env"))
secret_envs = {}
for secret_env_name in secret_envs_names:
    secret_envs[secret_env_name] = f"projects/{PROJECT_ID}/secrets/{secret_env_name}/versions/latest"

source_creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
target_creds = impersonated_credentials.Credentials(
    source_credentials=source_creds,
    target_principal=SERVICE_EMAIL,
    target_scopes=["https://www.googleapis.com/auth/cloud-platform"],
    lifetime=3600,
)

client = batch_v1.BatchServiceClient(credentials=target_creds)

parent = f"projects/{PROJECT_ID}/locations/{LOCATION}"
job_full_name = f"{parent}/jobs/{JOB_NAME}"

runnable = batch_v1.Runnable()
runnable.container = batch_v1.Runnable.Container()
runnable.container.image_uri = IMAGE_URI

task = batch_v1.TaskSpec()
task.runnables = [runnable]
task.environment = batch_v1.Environment()
task.environment.variables = container_envs
task.environment.secret_variables = secret_envs

resources = batch_v1.ComputeResource()
resources.cpu_milli = CPU_MILLI
resources.memory_mib = MEM_MIB
task.compute_resource = resources

task.max_run_duration = MAX_DURATION

group = batch_v1.TaskGroup()
group.task_count = 1
group.task_spec = task

policy = batch_v1.AllocationPolicy.InstancePolicy()
policy.machine_type = VIRTUAL_MACHINE
instances = batch_v1.AllocationPolicy.InstancePolicyOrTemplate()
instances.policy = policy
allocation_policy = batch_v1.AllocationPolicy()
allocation_policy.instances = [instances]

service_account = batch_v1.ServiceAccount()
service_account.email = SERVICE_EMAIL
allocation_policy.service_account = service_account

job = batch_v1.Job()
job.task_groups = [group]
job.allocation_policy = allocation_policy
job.logs_policy = batch_v1.LogsPolicy()
job.logs_policy.destination = batch_v1.LogsPolicy.Destination.CLOUD_LOGGING

create_request = batch_v1.CreateJobRequest()
create_request.job = job
create_request.job_id = JOB_NAME
create_request.parent = parent

client.create_job(create_request)
print(f"Created Batch job: {job_full_name}")
