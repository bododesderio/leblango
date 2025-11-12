#!/bin/sh
set -e

cd /app/backend

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput || true

DEBUG=${DEBUG:-False}

if [ "$DEBUG" = "False" ]; then
    echo "Starting Gunicorn (Production Mode) on port 6200..."
    exec gunicorn leblango.wsgi:application \
        --bind 0.0.0.0:6200 \
        --workers 4 \
        --threads 2 \
        --timeout 120 \
        --access-logfile - \
        --error-logfile - \
        --log-level info
else
    echo "Starting Django Dev Server (Development Mode) on port 6200..."
    exec python manage.py runserver 0.0.0.0:6200
fi
