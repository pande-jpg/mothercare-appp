from django.db import models
from django.contrib.auth.models import User


class MotherProfile(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=128, blank=True)
    package = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ServiceBooking(models.Model):
    SERVICE_CHOICES = [
        ("Cooking Service", "Cooking Service"),
        ("Home Cleaning", "Home Cleaning"),
        ("Laundry Service", "Laundry Service"),
        ("Grocery Delivery", "Grocery Delivery"),
        ("Nurse Home Visit", "Nurse Home Visit"),
        ("Doctor Consultation", "Doctor Consultation"),
    ]

    mother = models.ForeignKey(MotherProfile, on_delete=models.CASCADE)
    assigned_provider = models.ForeignKey(
        "ServiceProvider",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_bookings",
    )
    service = models.CharField(max_length=100, choices=SERVICE_CHOICES)
    booking_date = models.DateField()
    booking_time = models.CharField(max_length=50)
    address = models.TextField()
    note = models.TextField(blank=True)
    status = models.CharField(max_length=30, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mother.name} - {self.service}"


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    phone = models.CharField(max_length=15, blank=True)
    package = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.email


class EmergencyRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.CharField(max_length=50, blank=True)
    longitude = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=30, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.status}"


class PaymentRecord(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Paid", "Paid"),
        ("Failed", "Failed"),
        ("Refunded", "Refunded"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="Pending"
    )
    payment_reference = models.CharField(
        max_length=200,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.package}"


class ServiceProvider(models.Model):
    ROLE_CHOICES = [
        ("Cook", "Cook"),
        ("Cleaner", "Cleaner"),
        ("Laundry", "Laundry"),
        ("Grocery", "Grocery"),
        ("Nurse", "Nurse"),
        ("Doctor", "Doctor"),
    ]

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    qualification = models.CharField(max_length=200, blank=True)
    verified = models.BooleanField(default=False)
    available = models.BooleanField(default=True)
    service_area = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.role}"
