import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or update the MotherCare production staff administrator from environment variables."

    def handle(self, *args, **options):
        if os.environ.get("CREATE_ADMIN_ON_DEPLOY", "false").lower() != "true":
            self.stdout.write("MotherCare admin bootstrap is disabled.")
            return

        username = os.environ.get("ADMIN_USERNAME", "").strip().lower()
        email = os.environ.get("ADMIN_EMAIL", "").strip().lower()
        password = os.environ.get("ADMIN_PASSWORD", "")

        if not username or not email or not password:
            raise CommandError(
                "Set CREATE_ADMIN_ON_DEPLOY=true plus ADMIN_USERNAME, ADMIN_EMAIL and ADMIN_PASSWORD."
            )
        if len(password) < 8:
            raise CommandError("ADMIN_PASSWORD must be at least 8 characters long.")

        User = get_user_model()
        user = User.objects.filter(username=username).first()
        if user is None:
            user = User.objects.filter(email=email).first()

        created = user is None
        if created:
            user = User(username=username, email=email)

        user.email = email
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        action = "created" if created else "updated"
        self.stdout.write(self.style.SUCCESS(f"MotherCare admin account {action}: {username}"))
