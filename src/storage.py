"""Storage layer helper.

STORAGE_MODE=local (default): copies files into a local data lake folder (data/lake/raw, data/lake/cleaned).
STORAGE_MODE=s3: uploads to any S3-compatible service using boto3 (set S3_ENDPOINT, keys and bucket in .env).
"""
import os
import shutil

from config import STORAGE_MODE, S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET


def upload(local_path, key):
    if STORAGE_MODE == "s3":
        import boto3
        from botocore.exceptions import ClientError

        client = boto3.client(
            "s3",
            endpoint_url=S3_ENDPOINT or None,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY,
        )
        try:
            client.head_bucket(Bucket=S3_BUCKET)
        except ClientError:
            client.create_bucket(Bucket=S3_BUCKET)
        client.upload_file(local_path, S3_BUCKET, key)
        print(f"Uploaded {local_path} -> s3://{S3_BUCKET}/{key}")
    else:
        dest = os.path.join("data", "lake", key)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy(local_path, dest)
        print(f"Saved {local_path} -> {dest}")
