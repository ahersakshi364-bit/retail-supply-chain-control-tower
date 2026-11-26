
FROM apache/airflow:3.3.1

USER airflow

ARG AIRFLOW_VERSION=3.3.1
ARG PYTHON_VERSION=3.13

RUN pip install --no-cache-dir "prophet==1.3.0" \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
