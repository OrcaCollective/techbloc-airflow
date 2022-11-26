from typing import NamedTuple

from airflow.decorators import task


class RotationPeriod(NamedTuple):
    name: str
    count: int


@task()
def get_most_recent_backup(backups: list[str]) -> str:
    backups = sorted(backups, reverse=True)
    backups = [backup for backup in backups if not backup.endswith("/")]
    # Return only the prefix itself
    return backups[0].split("/")[-1]


@task()
def get_files_to_delete(
    backups: list[str],
    count: int,
) -> list[str]:
    backups = sorted(backups, reverse=True)
    backups = [backup for backup in backups if not backup.endswith("/")]
    return backups[count:]
