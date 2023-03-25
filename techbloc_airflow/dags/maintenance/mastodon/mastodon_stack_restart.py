"""
# Restart Mastodon stack

The Mastodon stack generates a ton of logs, which can quickly
overwhelm the local disk and fill up space. It's healthy practice
to restart the stack once a week to counteract this. Ideally this
would also be paired with a change to Docker's log retention
for the service as well.
"""
from datetime import datetime

from airflow.decorators import dag
from airflow.providers.ssh.operators.ssh import SSHOperator

import constants
from common import dag_utils


@dag(
    dag_id="mastodon_stack_restart",
    start_date=datetime(2023, 3, 1),
    schedule="@weekly",
    tags=["maintenance", "mastodon"],
    default_args=dag_utils.DEFAULT_DAG_ARGS,
    catchup=False,
    doc_md=__doc__,
)
def restart_stack():

    SSHOperator(
        task_id="restart_stack",
        ssh_conn_id=constants.SSH_MASTODON_CONN_ID,
        command="cd mastodon && docker-compose down && docker-compose up -d",
    )


restart_stack()
