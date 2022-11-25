import json
from datetime import datetime

import constants
from airflow.decorators import dag
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.ssh.operators.ssh import SSHOperator


SERVICES = [
    "1-312-hows-my-driving",
    "spd-data-watch",
    "OpenOversight",
    "spd-lookup",
]


for service in SERVICES:
    service_name = service.replace("-", "_")
    dag_id = f"deploy_{service_name}"

    @dag(
        dag_id=dag_id,
        start_date=datetime(2022, 11, 24),
        catchup=False,
        schedule=None,
        tags=["deployment"],
    )
    def deployment_dag():

        ssh_deploy = SSHOperator(
            task_id=f"deploy_{service_name}",
            ssh_conn_id=constants.SSH_MONOLITH_CONN_ID,
            command="cd {{ params.service }} && just deploy",
            # Note that AcceptEnv has to be set for IS_PROD on the host
            # or this will fail silently!!
            # https://airflow.apache.org/docs/apache-airflow-providers-ssh/stable/_api/airflow/providers/ssh/operators/ssh/index.html#airflow.providers.ssh.operators.ssh.SSHOperator  # noqa
            environment={"IS_PROD": "true"},
            params={
                "service": service,
            },
        )

        matrix_alert = SimpleHttpOperator(
            task_id=f"notify_{service_name}_deploy",
            http_conn_id=constants.MATRIX_WEBHOOK_CONN_ID,
            data=json.dumps(
                {
                    "key": "{{ var.value.matrix_webhook_api_key }}",
                    "body": f"Deployment complete for `{service}`",
                }
            ),
        )

        ssh_deploy >> matrix_alert

    deployment_dag()
