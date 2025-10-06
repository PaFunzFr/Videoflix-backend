#!/bin/sh

# Exit the script immediately if any command fails (good for catching errors early)
set -e

echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."

# -q means "quiet" (only output errors, no extra logs)
# This loop keeps running as long as 'pg_isready' is NOT successful (exit code != 0).
# => keep checking every second until the database is ready to accept connections.
while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -q; do
  echo "PostgreSQL is not available yet - sleeping for 1 second"
  sleep 1
done

echo "PostgreSQL is ready - continuing..."

# Run Django management commands:
# 1. collectstatic: gather all static files into STATIC_ROOT (needed in production)
# 2. makemigrations: create migration files for model changes (normally done in development)
# 3. migrate: apply all migrations to the database
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate

# Automatically create a Django superuser if it doesn't exist yet.
# The username, email, and password are read from environment variables.
# This is useful for setting up an admin account in a fresh environment.
python manage.py shell <<EOF
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'adminpassword')

if not User.objects.filter(username=username).exists():
    print(f"Creating superuser '{username}'...")
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created.")
else:
    print(f"Superuser '{username}' already exists.")
EOF

# Start a background worker (using django-rq)
# '&' runs it in the background so the script can continue
python manage.py rqworker default &

# Finally, start Gunicorn (the production WSGI server for Django).
# - exec replaces the current shell process with Gunicorn (important for Docker)
# - 0.0.0.0:8000 makes it reachable on all network interfaces
# - --reload automatically restarts Gunicorn when code changes (good for development, 
#   usually disabled in production for performance)
exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --reload
