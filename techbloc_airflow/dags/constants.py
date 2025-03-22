import os


SSH_MONOLITH_CONN_ID = "ssh_monolith"
SPACES_CONN_ID = os.getenv("SPACES_CONN_ID")
SPACES_BUCKET_NAME = os.getenv("SPACES_BUCKET_NAME", "")
# DigitalOcean Spaces has a common shared bucket for everything, whereas locally we
# have a separate bucket for each service. If the bucket name is defined, all keys
# will be prefixed with that.
SPACES_KEY_PREFIX = f"s3://{SPACES_BUCKET_NAME}/" if SPACES_BUCKET_NAME else "s3://"

MATRIX_WEBHOOK_CONN_ID = "matrix_webhook"
MATRIX_WEBHOOK_API_KEY = "matrix_webhook_api_key"
