from datetime import datetime

from airflow.decorators import dag, task, task_group
from airflow.operators.bash import BashOperator
from airflow.providers.amazon.aws.transfers.local_to_s3 import (
    LocalFilesystemToS3Operator,
)
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.utils.trigger_rule import TriggerRule

import constants
from common import dag_utils, matrix
from maintenance.backups.offsite_configs import OFFSITE_CONFIGS, OffsiteConfig


LOCAL_BACKUPS_FOLDER = "/opt/backups"
BUCKET_NAME = "monolith-backups"


@task_group
def backup_service(config: OffsiteConfig):
    local_backup = f"{LOCAL_BACKUPS_FOLDER}/{config.filename}"

    backup = SSHOperator(
        task_id=f"backup_{config.name}",
        ssh_conn_id=constants.SSH_MONOLITH_CONN_ID,
        command=config.command,
    )

    copy_to_local = BashOperator(
        task_id=f"copy_{config.name}_to_local",
        bash_command=f"scp monolith:{config.final_path} {local_backup}",
    )

    copy_to_spaces = LocalFilesystemToS3Operator(
        task_id=f"copy_local_{config.name}_to_spaces",
        aws_conn_id=constants.SPACES_CONN_ID,
        dest_bucket=BUCKET_NAME,
        dest_key=config.filename,
        replace=True,
        filename=local_backup,
    )

    @task
    def notify_backup_complete():
        matrix.send_message(
            f"{config.name} backup complete at: `s3://{BUCKET_NAME}/{config.filename}`"
        )

    restart_if_failed = SSHOperator(
        task_id=f"start_if_failed_{config.name}",
        ssh_conn_id=constants.SSH_MONOLITH_CONN_ID,
        command=f"cd {config.folder} && just up",
        trigger_rule=TriggerRule.ONE_FAILED,
    )

    (
        backup
        >> copy_to_local
        >> copy_to_spaces
        >> notify_backup_complete()
        >> restart_if_failed
    )


@dag(
    dag_id="offsite_backup",
    start_date=datetime(2025, 3, 15),
    schedule="0 3 * * 0",
    catchup=False,
    tags=["maintenance", "matrix", "openoversight", "backups"],
    default_args=dag_utils.DEFAULT_DAG_ARGS,
    doc_md="""
# Backup volume offsite

This DAG backs up a Docker volume using [loomchild/volume-backup](https://github.com/loomchild/volume-backup).
It then copies the backup to the local machine, then uploads it to Spaces.
""",
)
def backup_matrix():
    for config in OFFSITE_CONFIGS:
        backup_service.override(group_id=f"backup_service_{config.name}")(config)


backup_matrix()
