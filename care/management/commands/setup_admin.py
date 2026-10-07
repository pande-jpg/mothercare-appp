import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create or update the MotherCare production administrator."

    DEFAULT_USERNAME = "mothercareadmin"
    DEFAULT_EMAIL = "admin@mothercare.app"
    DEFAULT_PASSWORD = "MCAdmin#2026!"

    def handle(self, *args, **options):
        username = os.environ.get("ADMIN_USERNAME", self.DEFAULT_USERNAME).strip().lower()
        email = os.environ.get("ADMIN_EMAIL", self.DEFAULT_EMAIL).strip().lower()
        password = os.environ.get("ADMIN_PASSWORD", self.DEFAULT_PASSWORD)

        if not username or not email or not password:
            raise CommandError("Admin username, email and password are required.")
        if len(password) < 8:
            raise CommandError("Admin password must contain at least 8 characters.")

        User = get_user_model()
        user = User.objects.filter(username=username).first()
        if user is None:
            user = User.objects.filter(email=email).first()

        created = user is None
        if created:
            user = User(username=username, email=email)

        user.username = username
        user.email = email
        user.first_name = "MotherCare Admin"
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        action = "created" if created else "updated"
        self.stdout.write(self.style.SUCCESS(
            f"MotherCare admin account {action}: {username}"
        ))
