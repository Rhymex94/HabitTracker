#!/bin/sh
set -e

# Wait for DB to be ready (Postgres example)
if [ "$DB_HOST" ]; then
  echo "Waiting for database at $DB_HOST..."
  until pg_isready -h "$DB_HOST" -p "$DB_PORT" >/dev/null 2>&1; do
    sleep 1
  done
fi

# Run migrations
echo "Running database migrations..."
flask db upgrade

# Start the app
echo "Starting app..."
exec python run.py