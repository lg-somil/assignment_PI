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
export AIRFLOW_PROJ_DIR=$(dirname $(realpath $ENV_FILE))
export AIRFLOW_UID=$(id -u)

echo "Environment variables from $ENV_FILE have been exported."

cd airflow/

if docker compose version &>/dev/null; then
    echo "Using 'docker compose'"
    DOCKER_COMPOSE_COMMAND="docker compose up"
elif command -v docker-compose &>/dev/null; then
    echo "Using 'docker-compose'"
    DOCKER_COMPOSE_COMMAND="docker-compose up"
else
    echo "Neither 'docker-compose' nor 'docker compose' command is available."
    exit 1
fi


echo "Using $DOCKER_COMPOSE_COMMAND to run Airflow init."

# Run Docker Compose with 'airflow-init'
$DOCKER_COMPOSE_COMMAND --build airflow-init

# Check if the 'airflow-init' command was successful
if [ $? -eq 0 ]; then
    echo "'airflow-init' completed successfully."
    echo "Now running '$DOCKER_COMPOSE_COMMAND up' to start the services in detached mode."

    # Run Docker Compose in detached mode
    $DOCKER_COMPOSE_COMMAND --build 
else
    echo "'airflow-init' failed. Exiting without starting services."
    exit 1
fi
