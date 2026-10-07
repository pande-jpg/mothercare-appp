import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create or update the MotherCare production admin account."

    def handle(self, *args, **options):
        enabled = os.environ.get("CREATE_ADMIN_ON_DEPLOY", "").lower()

        if enabled != "true":
            self.stdout.write("Admin setup is disabled.")
            return

        username = os.environ.get("ADMIN_USERNAME", "").strip().lower()
        email = os.environ.get("ADMIN_EMAIL", "").strip().lower()
        password = os.environ.get("ADMIN_PASSWORD", "")

        if not username or not email or not password:
            raise RuntimeError(
                "ADMIN_USERNAME, ADMIN_EMAIL and ADMIN_PASSWORD "
                "must be configured."
            )

        if len(password) < 8:
            raise RuntimeError("ADMIN_PASSWORD must contain at least 8 characters.")

        User = get_user_model()

        user = User.objects.filter(username=username).first()

        if user is None:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            action = "created"
        else:
            user.email = email
            user.set_password(password)
            action = "updated"

        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"MotherCare admin account {action} successfully."
            )
        )
