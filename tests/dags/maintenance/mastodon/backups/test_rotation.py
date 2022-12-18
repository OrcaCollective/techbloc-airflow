import pytest

from maintenance.mastodon.backups import rotation


BACKUP_LIST = [
    "postgres/daily/",
    "postgres/weekly/",
    "postgres/",
    "postgres/2022-11-25_19-00-01_backup.dump",
    "postgres/2022-11-25_20-00-01_backup.dump",
    "postgres/2022-11-25_21-00-01_backup.dump",
    "postgres/2022-11-25_22-00-01_backup.dump",
    "postgres/2022-11-25_23-00-01_backup.dump",
    "postgres/2022-11-26_00-00-01_backup.dump",
    "postgres/2022-11-26_01-00-01_backup.dump",
    "postgres/2022-11-26_02-00-01_backup.dump",
    "postgres/2022-11-26_03-00-01_backup.dump",
    "postgres/2022-11-26_04-00-01_backup.dump",
    "postgres/2022-11-26_05-00-01_backup.dump",
    "postgres/2022-11-26_06-00-01_backup.dump",
    "postgres/2022-11-26_07-00-01_backup.dump",
    "postgres/2022-11-26_08-00-01_backup.dump",
    "postgres/2022-11-26_09-00-01_backup.dump",
    "postgres/2022-11-26_10-00-01_backup.dump",
    "postgres/2022-11-26_11-00-01_backup.dump",
    "postgres/2022-11-26_12-00-01_backup.dump",
    "postgres/2022-11-26_13-00-01_backup.dump",
    "postgres/2022-11-26_14-00-01_backup.dump",
    "postgres/2022-11-26_15-00-01_backup.dump",
    "postgres/2022-11-26_16-00-01_backup.dump",
    "postgres/2022-11-26_17-00-01_backup.dump",
]


@pytest.mark.parametrize(
    "backups, expected",
    [
        # Full backup list
        (BACKUP_LIST, "2022-11-26_17-00-01_backup.dump"),
        # Empty list
        pytest.param(
            [],
            None,
            marks=pytest.mark.raises(exception=ValueError),
        ),
        # Only directories
        pytest.param(
            BACKUP_LIST[:3],
            None,
            marks=pytest.mark.raises(exception=ValueError),
        ),
    ],
)
def test_get_most_recent_backup(backups, expected):
    actual = rotation.get_most_recent_backup.function(backups)
    assert actual == expected


@pytest.mark.parametrize(
    "backups, count, expected",
    [
        # Keep one
        (BACKUP_LIST, 1, BACKUP_LIST[3:-1]),
        # Keep several, should be last few
        (BACKUP_LIST, 5, BACKUP_LIST[3:-5]),
        # Keep all
        (BACKUP_LIST, len(BACKUP_LIST), []),
        # Emtpy input list
        ([], 10, []),
        # Don't keep any
        (BACKUP_LIST, 0, BACKUP_LIST[3:]),
    ],
)
def test_get_files_to_delete(backups, count, expected):
    actual = rotation.get_files_to_delete.function(backups, count)
    assert set(actual) == set(expected)
