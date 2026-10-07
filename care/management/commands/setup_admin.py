from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create or update the fixed MotherCare production administrator."

    # Fixed bootstrap credentials requested for the first production login.
    USERNAME = "mothercareadmin"
    EMAIL = "admin@mothercare.app"
    PASSWORD = "MCAdmin#2026!"

    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.filter(username=self.USERNAME).first()
        if user is None:
            user = User.objects.filter(email=self.EMAIL).first()

        created = user is None
        if created:
            user = User(username=self.USERNAME, email=self.EMAIL)

        user.username = self.USERNAME
        user.email = self.EMAIL
        user.first_name = "MotherCare Admin"
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(self.PASSWORD)
        user.save()

        action = "created" if created else "updated"
        self.stdout.write(self.style.SUCCESS(
            f"MotherCare admin account {action}: {self.USERNAME}"
        ))
