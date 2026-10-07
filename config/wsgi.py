"""WSGI config for the MotherCare project."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()

# Production safety net: repair/create the configured admin on service startup.
# This is idempotent and uses environment variables when supplied.
try:
    from django.contrib.auth import get_user_model
    from django.db import connection

    if connection.vendor:
        User = get_user_model()
        username = os.environ.get("ADMIN_USERNAME", "mothercareadmin").strip().lower()
        email = os.environ.get("ADMIN_EMAIL", "admin@mothercare.app").strip().lower()
        password = os.environ.get("ADMIN_PASSWORD", "MCAdmin#2026!")
        if username and email and password:
            user = User.objects.filter(username=username).first() or User.objects.filter(email=email).first()
            if user is None:
                user = User(username=username)
            user.username = username
            user.email = email
            user.first_name = "MotherCare Admin"
            user.is_active = True
            user.is_staff = True
            user.is_superuser = True
            user.set_password(password)
            user.save()
except Exception:
    # Never prevent the public website from starting if the database is temporarily unavailable.
    pass
