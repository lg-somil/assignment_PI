#!/bin/bash

# Ensure .env file exists
ENV_FILE="airflow/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "$ENV_FILE does not exist."
    exit 1
fi

# Export each variable in the .env file to the environment
export $(grep -v '^#' $ENV_FILE | xargs)

# Optionally, set the AIRFLOW_PROJ_DIR to the directory containing the .env file
export AIRFLOW_PROJ_DIR=$(dirname $(realpath $ENV_FILE))/airflow
export AIRFLOW_UID=$(id -u)

echo "Environment variables from $ENV_FILE have been exported."
