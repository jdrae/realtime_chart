#!/bin/bash
set -e

docker-entrypoint.sh postgres &

echo "Check PostgreSQL with -U $POSTGRES_USER -d $POSTGRES_DB"
until pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

echo "PostgreSQL is ready. Executing SQL files in sql..."
for file in sql/*.sql; do
  if [ -f "$file" ]; then
    echo "=== $file ==="
    cat "$file"
    echo
    psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$file"
  fi
  echo "Done $file"
done

echo "Creating cronjob..."
printenv | grep POSTGRES_ > /app/.env
crontab /app/cronjob
crontab -l
cron

wait
