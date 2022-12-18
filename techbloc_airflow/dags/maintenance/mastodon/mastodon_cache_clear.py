from datetime import datetime

import constants
from airflow.decorators import dag
from airflow.providers.ssh.operators.ssh import SSHOperator
from common import dag_utils


DAYS_TO_KEEP = 14


@dag(
    dag_id="mastodon_cache_clear",
    start_date=datetime(2022, 11, 10),
    schedule="@weekly",
    catchup=False,
    tags=["maintenance", "mastodon"],
    default_args=dag_utils.DEFAULT_DAG_ARGS,
    doc_md=f"""
# Clear Mastodon cache

[Source from @michael@mstdn.thms.uk](https://mstdn.thms.uk/@michael/109401019005701213):

> By default that cache doesn't ever appear to be cleared out, which not only leads to
> inherently unlimited growth, but is probably a #gdpr / data protection nightmare too.


This clears out old media data from the Mastodon cache.

While any day can be chosen for the number of days to keep, {DAYS_TO_KEEP} has been
chosen based on this text from the utility help:

> The --days option specifies how old preview cards have to be before they are removed.
> It defaults to 180 days. Since preview cards will not be re-fetched unless the link
> is re-posted after 2 weeks from last time, it is not recommended to delete preview
> cards within the last 14 days.
""",
)
def clear_cache():

    for item in ["preview_cards", "media"]:

        SSHOperator(
            task_id=f"clear_cache_{item}",
            ssh_conn_id=constants.SSH_MASTODON_CONN_ID,
            command=(
                "cd mastodon && "
                "docker-compose run --rm web bin/tootctl {{ params.item }} remove --days {{ params.days }}"  # noqa
            ),
            params={"item": item, "days": DAYS_TO_KEEP},
        )


clear_cache()
