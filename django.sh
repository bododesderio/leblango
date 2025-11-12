#!/bin/sh
set -e

cd /app/backend

echo "🚀 Applying migrations..."
python manage.py migrate --noinput

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput || true

echo "🌍 Starting Django server on port 6200..."
python manage.py runserver 0.0.0.0:6200
