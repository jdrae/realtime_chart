#!/bin/bash
set -e

docker-entrypoint.sh postgres &

echo "Check PostgreSQL with -U $POSTGRES_USER -d $POSTGRES_DB"
until pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

echo "PostgreSQL is ready. Executing SQL files in /sql..."

for f in /sql/*.sql; do
  echo "Running $f..."
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$f"
  echo "Done $f"
done

wait
