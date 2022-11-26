from airflow.decorators import task


@task()
def get_most_recent_backup(backups: list[str]) -> str:
    backups = sorted(backups, reverse=True)
    backups = [backup for backup in backups if not backup.endswith("/")]
    if not backups:
        raise ValueError("No backups found")
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
