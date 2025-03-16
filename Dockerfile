# Cannot use $PYTHON_VERSION because that is overwritten by the base image
# with the patch version (we only care about major and minor version)
ARG PROJECT_PY_VERSION
ARG PROJECT_AIRFLOW_VERSION

FROM apache/airflow:slim-${PROJECT_AIRFLOW_VERSION}-python${PROJECT_PY_VERSION}

# Build-time arguments, with sensible defaults
ARG REQUIREMENTS_FILE=requirements_prod.txt

# Path configurations
ENV AIRFLOW_HOME=/opt/airflow
ENV DAGS_FOLDER=${AIRFLOW_HOME}/techbloc_airflow/dags
ENV PYTHONPATH=${DAGS_FOLDER}

# Container optimizations
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_NO_COLOR=1

# Airflow/workflow configuration
ENV DATABASE_DIR=${AIRFLOW_HOME}/db/
ENV AIRFLOW__CORE__DAGS_FOLDER=${DAGS_FOLDER}
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__CORE__LOAD_DEFAULT_CONNECTIONS=False
ENV AIRFLOW__CORE__ENABLE_XCOM_PICKLING=True


USER root
RUN apt-get update && apt-get -yqq install \
    build-essential \
    libpq-dev \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*
RUN mkdir -p ${DATABASE_DIR} /home/airflow/.ipython/ /opt/ssh/ /opt/backups && \
    chown -R airflow ${DATABASE_DIR} /home/airflow/.ipython/ /opt/ssh/ /opt/backups
USER airflow

WORKDIR  ${AIRFLOW_HOME}
# Always add the prod req because the dev reqs depend on it for deduplication
COPY ${REQUIREMENTS_FILE} requirements_prod.txt ${AIRFLOW_HOME}/

# args go out of scope when a new build stage starts so it must be redeclared here
ARG PROJECT_PY_VERSION
ARG PROJECT_AIRFLOW_VERSION

# https://airflow.apache.org/docs/apache-airflow/stable/installation/installing-from-pypi.html#constraints-files
ARG CONSTRAINTS_FILE="https://raw.githubusercontent.com/apache/airflow/constraints-${PROJECT_AIRFLOW_VERSION}/constraints-${PROJECT_PY_VERSION}.txt"

RUN pip install -r ${REQUIREMENTS_FILE} -c ${CONSTRAINTS_FILE}

COPY entrypoint.sh /opt/airflow/entrypoint.sh

ENTRYPOINT ["/usr/bin/dumb-init", "--", "/opt/airflow/entrypoint.sh"]
