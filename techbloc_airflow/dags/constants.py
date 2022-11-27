from datetime import timedelta

from common import matrix


SSH_MASTODON_CONN_ID = "ssh_mastodon"
SSH_MONOLITH_CONN_ID = "ssh_monolith"

MATRIX_WEBHOOK_CONN_ID = "matrix_webhook"
MATRIX_WEBHOOK_API_KEY = "matrix_webhook_api_key"


DEFAULT_DAG_ARGS = {
    "catchup": False,
    "owner": "techbloc",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(hours=1),
    "on_failure_callback": matrix.on_failure_callback,
}
