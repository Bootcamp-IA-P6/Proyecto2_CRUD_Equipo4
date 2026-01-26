#!/bin/bash
set -e

echo "⏳ Waiting for database..."

# Esperar a MySQL
until alembic current >/dev/null 2>&1; do
  sleep 2
done

echo "📦 Running Alembic migrations..."
alembic upgrade head

echo "🚀 Starting FastAPI..."
exec "$@"   #
