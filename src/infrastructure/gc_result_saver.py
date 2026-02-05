from google.cloud import storage


class GoogleCloudResultSaver:
    def __init__(self, bucket_name: str = "llm-reasoning-benchmark-results"):
        client = storage.Client()
        self._bucket = client.bucket(bucket_name)

    def save_result(self, file_name: str, benchmark_result: str):
        blob = self._bucket.blob(file_name)

        blob.upload_from_string(benchmark_result, content_type="application/json")

    def get_result(self, file_name: str) -> str:
        blob = self._bucket.blob(file_name)

        benchmark_result = blob.download_as_string()
        benchmark_result = benchmark_result.decode(encoding="utf-8")
        return benchmark_result
