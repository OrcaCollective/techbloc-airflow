#!/bin/bash
# DAG sync script used in production to update the repo files when invoked.
# This can be run using cron at the desired DAG sync interval.
# Lifted from https://github.com/WordPress/openverse-catalog/blob/main/dag-sync.sh
#
# Inputs:
#   - The first argument to the script should be the Matrix room URL target
#     for the output sync message.
#   - The second argument is the API key needed to interact with the webhook server
# (test change please ignore)
#
# Inspired by https://stackoverflow.com/a/21005490/3277713 via torek CC BY-SA 3.0
set -e

MATRIX_ROOM=$1
MATRIX_KEY=$2
# https://stackoverflow.com/a/246128 via Dave Dopson CC BY-SA 4.0
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR"

# Update origin
git fetch origin
# Get new commit hash *one commit ahead* of this one
new=$(git rev-list --reverse --topo-order HEAD..origin/feature/dag-sync-webhook | head -1)
# If there is no new commit hash to move to, nothing has changed, quit early
[ -z "$new" ] && exit

# Move ahead to this new commit
git reset --hard "$new"
# Verify if have /dags/ in the last commit
have_dag="true"  # $(git log -p -1 "$new"  --pretty=format: --name-only | grep "/dags/")
# If there is no files under /dags/ folder, no need to notify, quit early
[ -z "$have_dag" ] && exit

# Pull out the subject from the new commit
subject=$(git log -1 --format='%s')

if [ -z "$MATRIX_ROOM" ]
  then
  echo "Matrix room was not supplied! Updates will not be posted"
else
  curl "$MATRIX_ROOM" \
    -d '{"body":"DAG synced: ['"$subject"'](https://github.com/OrcaCollective/techbloc-airflow/commit/'"$new"')", "key": "'"$MATRIX_KEY"'"}'
fi
