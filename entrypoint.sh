#!/bin/bash

set -e

function help_text() {
  cat << 'END'
 _____         _      ______ _               ___  _       __ _
|_   _|       | |     | ___ \ |             / _ \(_)     / _| |
  | | ___  ___| |__   | |_/ / | ___   ___  / /_\ \_ _ __| |_| | _____      __
  | |/ _ \/ __| '_ \  | ___ \ |/ _ \ / __| |  _  | | '__|  _| |/ _ \ \ /\ / /
  | |  __/ (__| | | | | |_/ / | (_) | (__  | | | | | |  | | | | (_) \ V  V /
  \_/\___|\___|_| |_| \____/|_|\___/ \___| \_| |_/_|_|  |_| |_|\___/ \_/\_/

Docker entrypoint script for Tech Bloc Airflow. This uses the upstream Airflow
entrypoint under the hood. For help running commands, see
https://airflow.apache.org/docs/docker-stack/entrypoint.html#executing-commands
Unless specified, all commands will wait for the database to be ready and
will upgrade the Airflow schema.

Usage:
  help - print this help text and exit
  bash [...] - drop into a bash shell or run a bash command/script
  python [ ... ] - drop into a python shell or run a python command/script
  (anything else) - interpreted as an argument to "airflow [ argument ]"
END
}


function header() {
  size=${COLUMNS:-80}
  # Print centered text between two dividers of length $size
  printf '#%.0s' $(seq 1 $size) && echo
  printf "%*s\n" $(( (${#1} + size) / 2)) "$1"
  printf '#%.0s' $(seq 1 $size) && echo
}

if [ "$1" == help ] || [ "$1" == --help ]; then help_text && exit 0; fi
sleep 0.1;  # The $COLUMNS variable takes a moment to populate

# Reformat Airflow connections that use https
header "MODIFYING ENVIRONMENT"
# Loop through environment variables, relying on naming conventions.
# Bash loops with pipes occur in a subprocess, so we need to do some special
# subprocess manipulation via <(...) syntax to allow the `export` calls
# to propagate to the outer shell.
# See: https://unix.stackexchange.com/a/402752
while read -r var_string; do
    # get the variable name
    var_name=$(expr "$var_string" : '^\([A-Z_]*\)')
    echo "Variable Name: $var_name"
    # get the old value
    old_value=$(expr "$var_string" : '^[A-Z_]*=\(http.*\)$')
    echo "    Old Value: $old_value"
    # call python to url encode the http clause
    url_encoded=$(python -c "from urllib.parse import quote_plus; import sys; print(quote_plus(sys.argv[1]))" "$old_value")
    # prepend https://
    new_value='https://'$url_encoded
    echo "    New Value: $new_value"
    # set the environment variable
    export "$var_name"="$new_value"
# only include airflow connections with http somewhere in the string
done < <(env | grep "^AIRFLOW_CONN[A-Z_]\+=http.*$")

header "COPYING SSH FILES"

mkdir -p /home/airflow/.ssh/
if [ -n "$(ls -A /opt/ssh/ 2>/dev/null)" ]
then
    cp /opt/ssh/* /home/airflow/.ssh/
else
    echo "!!!!! NOTE: Mounted ssh directory /opt/ssh/ is empty, ssh operations may fail !!!!!"
fi
chown -R airflow /home/airflow/.ssh/

# This script is run as root, but everything hereafter we want to run as
# the airflow user. This is done so that permissions with the host can be
# managed appropriately.
exec runuser -u airflow -- /entrypoint "$@"
