#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate

# Optional one-time production admin bootstrap.
# It does nothing unless CREATE_ADMIN_ON_DEPLOY=true is configured in Render.
if [ "${CREATE_ADMIN_ON_DEPLOY:-false}" = "true" ]; then
  python manage.py setup_admin
fi
