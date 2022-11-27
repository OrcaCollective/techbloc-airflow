from datetime import timedelta

from common import matrix


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
