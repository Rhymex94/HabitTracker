#!/bin/sh
set -e

# Wait for database to be ready
echo "Waiting for database..."
until python -c "
import os
import pymysql
from urllib.parse import urlparse

url = urlparse(os.environ['DATABASE_URL'])
pymysql.connect(
    host=url.hostname,
    port=url.port or 3306,
    user=url.username,
    password=url.password,
    connect_timeout=2
)
" 2>/dev/null; do
    echo "Database not ready, retrying in 2 seconds..."
    sleep 2
done
echo "Database is ready!"

# Run migrations
echo "Running database migrations..."
flask db upgrade

# Start the app
echo "Starting app..."
exec python run.py
