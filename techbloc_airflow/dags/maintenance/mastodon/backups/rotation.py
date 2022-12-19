from airflow.decorators import task


def _filter_top_level(backups: list[str], top_level: bool) -> list[str]:
    backups = sorted(backups, reverse=True)
    # Only get actual files
    backups = [backup for backup in backups if not backup.endswith("/")]
    if top_level:
        # Only get files from the top level prefix
        backups = [backup for backup in backups if backup.count("/") == 1]
    return backups


@task()
def get_most_recent_backup(backups: list[str]) -> str:
    backups = _filter_top_level(backups, top_level=True)
    if not backups:
        raise ValueError("No backups found")
    # Return only the prefix itself
    return backups[0].split("/")[-1]


@task()
def get_files_to_delete(
    backups: list[str],
    count: int,
    top_level: bool = False,
) -> list[str]:
    backups = _filter_top_level(backups, top_level=top_level)
    return backups[count:]
