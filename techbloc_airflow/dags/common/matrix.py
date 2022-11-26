import json

import constants
from airflow.models import Variable
from airflow.providers.http.hooks.http import HttpHook


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
    api_key = api_key or Variable.get(constants.MATRIX_WEBHOOK_API_KEY)
    hook.run(
        data=json.dumps(
            {
                "key": api_key,
                "body": f"**[Airflow {environment}]**\n {text}",
            }
        )
    )
