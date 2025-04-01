#!/bin/bash
set -e

echo "Checking database schema..."
python src/execute_sql.py

echo "Starting Flask app..."
exec python src/app.py
