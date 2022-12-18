from datetime import datetime

import constants
from airflow.decorators import dag, task
from airflow.providers.ssh.operators.ssh import SSHOperator
from common import dag_utils, matrix


DAYS_TO_KEEP = 14


@dag(
    dag_id="openoversight_backup",
    start_date=datetime(2022, 11, 10),
    schedule="@weekly",
    catchup=False,
    tags=["maintenance", "openoversight", "backups"],
    default_args=dag_utils.DEFAULT_DAG_ARGS,
    doc_md="""
# Backup OpenOversight database

This DAG backs up the OpenOversight database using an existing `just` command on the
instance.
""",
)
def backup_openoversight():

    backup = SSHOperator(
        task_id="backup_openoversight",
        ssh_conn_id=constants.SSH_MONOLITH_CONN_ID,
        command="cd OpenOversight && just backup ~/backups/",
    )

    get_count = SSHOperator(
        task_id="get_backup_count",
        ssh_conn_id=constants.SSH_MONOLITH_CONN_ID,
        do_xcom_push=True,
        command="ls -l ~/backups/openoversight-postgres-*.tar.bz2 | wc -l",
    )

    @task
    def notify_backup_count(count: bytes):
        matrix.send_message(
            f"OpenOversight backup complete! "
            f"Total backups: `{count.decode('utf-8').strip()}`"
        )

    notify_backup_count(get_count.output)

    backup >> get_count


backup_openoversight()
