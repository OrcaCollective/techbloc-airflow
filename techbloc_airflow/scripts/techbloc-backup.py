#!/usr/bin/env python

import logging
import os

import boto3


FILENAMES = [f"{name}-backup.tar.bz2" for name in ["matrix", "openoversight"]]
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR")
SPACES_BUCKET_NAME = os.getenv("SPACES_BUCKET_NAME")
SPACES_BASE_PREFIX = "monolith-backups"


log = logging.getLogger(__name__)


def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=os.getenv("SPACES_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("SPACES_SECRET_KEY"),
        endpoint_url="https://sfo3.digitaloceanspaces.com",
        region_name="sfo3",
    )


def download_files():
    client = get_s3_client()
    for filename in FILENAMES:
        key = f"{SPACES_BASE_PREFIX}/{filename}"
        download_path = f"{DOWNLOAD_DIR}/{filename}"
        log.info(f"Downloading {filename} to {download_path}")

        client.download_file(SPACES_BUCKET_NAME, key, download_path)
    log.info(f"Downloaded {len(FILENAMES)} files")


if __name__ == "__main__":
    logging.basicConfig(
        format="[%(asctime)s - %(name)s - %(lineno)3d][%(levelname)s] %(message)s",
        level=logging.INFO,
    )
    download_files()
