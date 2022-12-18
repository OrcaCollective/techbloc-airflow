from datetime import datetime
from typing import NamedTuple

from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.operators.s3 import (
    S3CopyObjectOperator,
    S3DeleteObjectsOperator,
    S3ListOperator,
)
from airflow.utils.task_group import TaskGroup

import constants
from common import dag_utils, matrix
from maintenance.mastodon.backups import rotation


class RotationPeriod(NamedTuple):
    name: str
    count: int


BUCKET_NAME = "mastadon-backups"
PERIODS = [
    RotationPeriod("hourly", 24),
    RotationPeriod("daily", 7),
    RotationPeriod("weekly", 4),
]


for period in PERIODS:
    dag_id = f"mastodon_rotate_backup_{period.name}"

    @dag(
        dag_id=dag_id,
        start_date=datetime(2022, 11, 24),
        catchup=False,
        schedule=f"@{period.name}",
        tags=["maintenance", "backups", "mastodon"],
        default_args=dag_utils.DEFAULT_DAG_ARGS,
    )
    def backup_dag():
        for service in ["postgres", "redis", "user-media"]:
            with TaskGroup(group_id=f"rotate_{service}"):

                # Hourly backups are stored in the root of the bucket, whereas backups
                # by period are stored in a prefix by that period name
                prefix = (
                    f"{service}/{period.name}/"
                    if period.name != "hourly"
                    else f"{service}/"
                )

                # While these are defined first in the DAG, they're actually the last
                # steps. They need to be defined here to be used in the flow below.
                list_period_keys = S3ListOperator(
                    task_id=f"list_existing_{period.name}_backups_{service}",
                    aws_conn_id=constants.SPACES_MASTODON_CONN_ID,
                    bucket=BUCKET_NAME,
                    prefix=prefix,
                )

                get_delete_files = rotation.get_files_to_delete.override(
                    task_id=f"get_files_to_delete_{service}"
                )(list_period_keys.output, period.count)

                delete_old_backups = S3DeleteObjectsOperator(
                    task_id=f"delete_old_backups_{service}",
                    aws_conn_id=constants.SPACES_MASTODON_CONN_ID,
                    bucket=BUCKET_NAME,
                    keys=get_delete_files,
                )

                list_period_keys >> get_delete_files >> delete_old_backups

                # Hourly backups don't require archiving
                if period.name != "hourly":
                    list_keys = S3ListOperator(
                        task_id=f"list_existing_hourly_backups_{service}",
                        aws_conn_id=constants.SPACES_MASTODON_CONN_ID,
                        bucket=BUCKET_NAME,
                        prefix=f"{service}/",
                    )

                    most_recent_backup = rotation.get_most_recent_backup.override(
                        task_id=f"get_most_recent_backup_{service}"
                    )(list_keys.output)

                    copy_most_recent = S3CopyObjectOperator(
                        task_id=f"copy_most_recent_backup_{service}",
                        aws_conn_id=constants.SPACES_MASTODON_CONN_ID,
                        source_bucket_name=BUCKET_NAME,
                        dest_bucket_name=BUCKET_NAME,
                        source_bucket_key=f"{service}/{most_recent_backup}",
                        dest_bucket_key=f"{service}/{period.name}/{most_recent_backup}",
                    )

                    notify_complete = PythonOperator(
                        task_id=f"notify_{service}_{period.name}_complete",
                        python_callable=matrix.send_message,
                        op_kwargs={
                            "text": f"Mastodon: {period.name.capitalize()} `{service}` "
                            "backup rotations complete"
                        },
                    )

                    most_recent_backup >> copy_most_recent >> list_period_keys
                    delete_old_backups >> notify_complete

    backup_dag()
