#!/bin/bash
set -e

docker-entrypoint.sh postgres &

echo "Check PostgreSQL with -U $POSTGRES_USER -d $POSTGRES_DB"
until pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

echo "PostgreSQL is ready. Executing SQL files in /sql..."

for file in /sql/*.sql; do
  if [ -f "$file" ]; then
    echo "=== $file ==="
    cat "$file"
    echo
  fi
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$file"
  echo "Done $file"
done

wait
