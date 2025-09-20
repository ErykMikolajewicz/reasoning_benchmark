# Documentation for Running the Benchmark in the Cloud

## Limitations

- Currently, the project contains **only scripts** to run the benchmark on **Google Cloud Platform (GCP)**.  
- You need **your own language model keys** and a **GCP account**. The user covers the infrastructure costs (e.g., the virtual machine on which the tests are run).  
- Cloud operating costs are **minimal** – usually below **10 cents per run**. The main expense is the usage fees of **language models**.  
- A cost comparison for different models can be found in the **`README.md`** file.

---

## Preliminary Information

- Scripts were tested on **Linux**. They should work on **Windows** with minor modifications.  
- **Podman** is required to build the container image.  
- It is probably possible to build the image using **Docker**, but this requires changes in the `add_image.py` script.  
- You must have the **`gcloud` CLI** tool (Google’s official tool for managing GCP) installed and configured.  
- Install the libraries from the **`pyproject.toml`** file using tools like `pip` or `uv`.

---

## Step-by-Step Instructions

### 1. Configure Environment Variables
- Rename the file **`.env.example`** in the `cloud_run` folder to **`.env`**.  
- Fill it in with the appropriate data.

### 2. Create a Project in GCP
- Run the script **`create_project.sh`**.  
- After installation, you will get a link to the **Secrets** tab in Google Cloud Platform – follow it.

### 3. Configure Model Keys
- In **Google Cloud Platform Secret Manager**, add your language model keys.  
- Name them according to the example in `settings_example/api_keys.env`, e.g.:  
  ```
  GEMINI_API_KEY
  ```

### 4. Prepare the Configuration
- Rename the **`settings_example`** folder to **`settings`**.  
- Fill in the configuration files.  
- You don’t need to fill in `api_keys.env` if you use GCP Secret Manager – but its structure defines the secret names, so keep the format, e.g.:  
  ```env
  OPENAI_API_KEY=null
  ```

### 5. Build the Container Image
- Podman:
  ```bash
  podman image build --tag reasoning_benchmark .
  ```

### 6. Add the Image to the Repository
- Run the script:  
  ```bash
  cloud_run/add_image.py
  ```

### 7. Run the Benchmark
- Start the tests with:  
  ```bash
  cloud_run/run_benchmark_in_batch.py
  ```

### 8. Monitor Progress
- Progress can be tracked in the **Batch** tab of Google Cloud Platform:  
  [https://console.cloud.google.com/batch/jobs](https://console.cloud.google.com/batch/jobs)