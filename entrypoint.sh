#!/bin/sh

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating cache table if needed..."
python manage.py createcachetable --database=default

echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000
