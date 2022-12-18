import json
import logging

import constants
from airflow.exceptions import AirflowNotFoundException
from airflow.models import Variable
from airflow.providers.http.hooks.http import HttpHook


log = logging.getLogger(__name__)


def should_send_message(
    environment: str,
    http_conn_id: str = constants.MATRIX_WEBHOOK_CONN_ID,
):
    """
    Returns True if:
      * A Matrix connection is defined
      * We are in the prod env OR the message override is set.
    """
    # Exit early if no slack connection exists
    hook = HttpHook(http_conn_id=http_conn_id)
    try:
        hook.get_conn()
    except AirflowNotFoundException:
        return False

    # Exit early if we aren't on production or if force alert is not set
    force_message = Variable.get(
        "SLACK_MESSAGE_OVERRIDE", default_var=False, deserialize_json=True
    )
    return environment == "prod" or force_message


def send_message(
    text: str,
    conn_id: str = constants.MATRIX_WEBHOOK_CONN_ID,
    api_key: str = None,
) -> None:
    """
    Send a message to Matrix using a connection ID and API key.
    """
    hook = HttpHook(method="POST", http_conn_id=conn_id)
    environment = Variable.get("ENVIRONMENT", default_var="dev")
    if not should_send_message(environment, http_conn_id=conn_id):
        log.info("Not sending message to Matrix")
        return

    api_key = api_key or Variable.get(constants.MATRIX_WEBHOOK_API_KEY)
    hook.run(
        data=json.dumps(
            {
                "key": api_key,
                "body": f"**[Airflow {environment}]**\n {text}",
            }
        )
    )


def on_failure_callback(context: dict) -> None:
    """
    Send an alert out regarding a failure to Matrix.
    Errors are only sent out in production and if a Matrix connection is defined.
    """
    # Get relevant info
    ti = context["task_instance"]
    execution_date = context["execution_date"]
    exception: Exception | None = context.get("exception")
    exception_message = ""

    if exception:
        # Forgo the alert on upstream failures
        if (
            isinstance(exception, Exception)
            and "Upstream task(s) failed" in exception.args
        ):
            log.info("Forgoing Matrix alert due to upstream failures")
            return
        exception_message = f"""
*Exception*: {exception}\n
*Exception Type*: `{exception.__class__.__module__}.{exception.__class__.__name__}`\n
"""

    message = f"""
*DAG*: `{ti.dag_id}`\n
*Task*: `{ti.task_id}`\n
*Execution Date*: {execution_date.strftime('%Y-%m-%dT%H:%M:%SZ')}\n
*Log*: {ti.log_url}\n
{exception_message}
"""
    send_message(message)
