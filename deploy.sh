#!/bin/bash

set -euo pipefail

cd /home/openclaw/Backend-FastAPI-Hackathon-KIC

DB_HOST="localhost"
DB_PORT="5432"
DB_USER="kic_user"
DB_NAME="iot_fuzzy_kideco"
DB_PASSWORD="kic_user01"

run_psql() {
  PGPASSWORD="$DB_PASSWORD" psql \
    -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
    -v ON_ERROR_STOP=1 "$@"
}

echo "Pull latest code..."
git pull

echo "Activate virtual environment..."
source .venv/bin/activate

echo "Preparing migration history..."
run_psql -c "
  CREATE TABLE IF NOT EXISTS schema_migrations (
    filename VARCHAR(255) PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
  );
"

if [ "$(run_psql -tAc "SELECT to_regclass('public.devices') IS NOT NULL;")" != "t" ]; then
  echo "Database baru terdeteksi; menerapkan schema utama..."
  run_psql -f database/schema.sql
fi

echo "Applying pending database migrations..."
for migration in database/migrations/*.sql; do
  [ -e "$migration" ] || continue

  migration_name="$(basename "$migration")"
  applied="$(run_psql -tAc "SELECT EXISTS (SELECT 1 FROM schema_migrations WHERE filename = '$migration_name');")"

  if [ "$applied" = "t" ]; then
    echo "Migration sudah diterapkan: $migration_name"
    continue
  fi

  echo "Menjalankan migration: $migration_name"
  run_psql -f "$migration"
  run_psql -c "INSERT INTO schema_migrations (filename) VALUES ('$migration_name');"
done

echo "Install/update dependencies..."
pip install -r requirements.txt

echo "Restart SIMOSI API service..."
sudo systemctl restart simosi-api

echo "Check service status..."
sudo systemctl status simosi-api --no-pager -l

echo "Deploy finished."
