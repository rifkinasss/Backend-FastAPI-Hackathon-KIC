#!/bin/bash

set -e

cd /home/openclaw/Backend-FastAPI-Hackathon-KIC

echo "Pull latest code..."
git pull

echo "Activate virtual environment..."
source .venv/bin/activate

echo "Updating database schema..."
PGPASSWORD="kic_user01" psql -h localhost -p 5432 -U kic_user -d iot_fuzzy_kideco -f database/schema.sql

echo "Install/update dependencies..."
pip install -r requirements.txt

echo "Restart SIMOSI API service..."
sudo systemctl restart simosi-api

echo "Check service status..."
sudo systemctl status simosi-api --no-pager -l

echo "Deploy finished."
