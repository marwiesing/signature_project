#!/bin/bash
set -e

echo "Checking database schema..."
python src/execute_sql.py

echo "Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:5000 "src.app:create_app()"
