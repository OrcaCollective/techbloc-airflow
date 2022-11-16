set dotenv-load := false

# Show all available recipes
default:
  @just --list --unsorted

IS_PROD := env_var_or_default("IS_PROD", "")
DOCKER_FILES := "--file=docker-compose.yml" + (
    if IS_PROD != "true" {" --file=docker-compose.override.yml"} else {""}
)
SERVICE := env_var_or_default("SERVICE", "scheduler")

export PROJECT_PY_VERSION := `grep '# PYTHON' requirements_prod.txt | awk -F= '{print $2}'`
export PROJECT_AIRFLOW_VERSION := `grep '^apache-airflow' requirements_prod.txt | awk -F= '{print $3}'`

# Print the required Python version
@py-version:
    echo $PROJECT_PY_VERSION

# Print the current Airflow version
@airflow-version:
    echo $PROJECT_AIRFLOW_VERSION

# Check the installed Python version matches the required Python version and fail if not
check-py-version:
    #! /usr/bin/env sh
    installed_python_version=`python -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")'`
    if [ "$PROJECT_PY_VERSION" != "$installed_python_version" ]
    then
        printf "Detected Python version $installed_python_version but $PROJECT_PY_VERSION is required.\n" > /dev/stderr
        exit 1
    fi

# Install dependencies into the current environment
install: check-py-version
    pip install -r requirements_tooling.txt -r requirements_dev.txt
    pre-commit install

# Create the .env file from the template
dotenv:
    @([ ! -f .env ] && cp env.template .env) || true

# Run docker compose with the specified command
_dc *args:
    docker-compose {{ DOCKER_FILES }} {{ args }}

# Build all (or specified) container(s)
build service="": dotenv
    @just _dc build {{ service }}

# Bring all Docker services up
up flags="": dotenv
    @just _dc up -d {{ flags }}

# Take all Docker services down
down flags="":
    @just _dc down {{ flags }}

# Recreate all volumes and containers from scratch
recreate: dotenv
    @just down -v
    @just up "--force-recreate --build"

# Show logs of all, or named, Docker services
logs service="": up
    @just _dc logs -f {{ service }}

# Pull, build, and deploy all services
deploy:
    @just down
    -git pull
    @just build
    @just up

# Run pre-commit on all files
lint:
    pre-commit run --all-files

# Load any dependencies necessary for actions on the stack without running the webserver
_deps:
    @just up "s3"

# Mount the tests directory and run a particular command
@_mount-tests command: _deps
    # The test directory is mounted into the container only during testing
    @just _dc run \
        -v {{ justfile_directory() }}/tests:/opt/airflow/tests/ \
        -v {{ justfile_directory() }}/pytest.ini:/opt/airflow/pytest.ini \
        --rm \
        {{ SERVICE }} \
        {{ command }}

# Run a container that can be used for repeated interactive testing
test-session:
    @just _mount-tests bash

# Run pytest using the webserver image
test *pytestargs:
    @just _mount-tests "bash -c \'pytest {{ pytestargs }}\'"

# Open a shell into the webserver container
shell: up
    @just _dc exec {{ SERVICE }} /bin/bash

# Launch an IPython REPL using the webserver image
ipython: _deps
    @just _dc run \
        --rm \
        -w /opt/airflow/techbloc_airflow/dags \
        {{ SERVICE }} \
        bash -c \'ipython\'

# Run a given command in bash using the scheduler image
run *args: _deps
    @just _dc run --rm {{ SERVICE }} bash -c \'{{ args }}\'

# Launch a pgcli shell on the postgres container (defaults to openledger) use "airflow" for airflow metastore
db-shell:
    @just run bash -c 'sqlite3 /opt/airflow/db/airflow.db'
