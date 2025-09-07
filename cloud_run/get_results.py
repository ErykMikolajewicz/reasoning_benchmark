from pathlib import Path

from google.cloud import storage


def get_benchmark_results(bucket_name: str, target_dir: str):
    client = storage.Client.create_anonymous_client()
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs()
    target_dir = Path(target_dir)
    for blob in blobs:
        path = target_dir / blob.name
        path.parent.mkdir(parents=True, exist_ok=True)
        blob.download_to_filename(path)

if __name__ == "__main__":
    get_benchmark_results("llm-reasoning-benchmark-results", "../results")
