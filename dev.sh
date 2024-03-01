#!/bin/bash

is_service_running() {
    local service_name="$1"
    docker compose ps --services --filter "status=running" | grep -q "^$service_name$"
}

is_venv_activated() {
    [[ "$VIRTUAL_ENV" != "" ]]
}

if ! is_service_running "db"; then
    echo "Starting PostgreSQL database..."
    docker compose up -d db
else
    echo "PostgreSQL database is already running."
fi

if ! is_service_running "pgadmin"; then
    echo "Starting pgAdmin container..."
    docker compose up -d pgadmin
else
    echo "pgAdmin container is already running."
fi

if ! is_service_running "storage-service"; then
    echo "Starting storage-service container..."
    docker compose up -d storage-service
else
    echo "Storage-service container is already running."
fi

if ! is_venv_activated; then
    echo "Activating virtual environment..."
    source env/bin/activate
else
    echo "Virtual environment is already activated."
fi

echo "Starting Flask app..."
flask run

FLASK_EXIT_CODE=$?

if [ $FLASK_EXIT_CODE -eq 0 ]; then
    echo "Flask exited successfully. Stopping Docker containers..."
    docker compose stop
else
    echo "Flask exited with an error. Check logs for details."
fi
