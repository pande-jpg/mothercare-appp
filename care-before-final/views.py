from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from datetime import date

from .models import (
    EmergencyRequest,
    MotherProfile,
    Notification,
    PaymentRecord,
    Review,
    ServiceBooking,
    ServiceProvider,
    UserProfile,
)

PACKAGE_PRICES = {
    "Basic Care": 16000,
    "MotherCare Plus": 24000,
    "Premium Care": 35000,
}


def create_notification(user, title, message):
    Notification.objects.create(user=user, title=title, message=message)


def home(request):
    profile = None
    bookings = []
    emergencies = []
    notifications = []

    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        try:
            mother = MotherProfile.objects.get(email=request.user.email)
            bookings = (
                ServiceBooking.objects.filter(mother=mother)
                .select_related("assigned_provider")
                .order_by("-created_at")
            )
        except MotherProfile.DoesNotExist:
            bookings = []
        emergencies = EmergencyRequest.objects.filter(user=request.user).order_by("-created_at")
        notifications = Notification.objects.filter(user=request.user)[:10]

    return render(
        request,
        "home.html",
        {
            "user": request.user,
            "profile": profile,
            "bookings": bookings,
            "emergencies": emergencies,
            "notifications": notifications,
        },
    )


def register(request):
    if request.method != "POST":
        return redirect("/#register")

    name = request.POST.get("name", "").strip()
    email = request.POST.get("email", "").strip().lower()
    phone = request.POST.get("phone", "").strip()
    password = request.POST.get("password", "")

    if not name or not email or not phone or not password:
        messages.error(request, "Please fill all registration fields.")
        return redirect("/#register")
    if len(password) < 8:
        messages.error(request, "Password must be at least 8 characters.")
        return redirect("/#register")
    if User.objects.filter(username=email).exists():
        messages.error(request, "An account with this email already exists.")
        return redirect("/#register")

    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=name,
    )
    UserProfile.objects.create(user=user, phone=phone)
    MotherProfile.objects.update_or_create(
        email=email,
        defaults={"name": name, "phone": phone},
    )
    create_notification(user, "Welcome to MotherCare", "Your MotherCare account is ready.")
    messages.success(request, "Account created successfully.")
    return redirect("/#profile")


def login_user(request):
    if request.method != "POST":
        return redirect("/")

    email = request.POST.get("email", "").strip().lower()
    password = request.POST.get("password", "")
    user = authenticate(request, username=email, password=password)

    if user is not None:
        login(request, user)
        messages.success(request, "Welcome back to MotherCare!")
        return redirect("/#dashboard")

    messages.error(request, "Invalid email or password.")
    return redirect("/#account")


def logout_user(request):
    logout(request)
    return redirect("/")


@login_required
def choose_package(request, package_name):
    if package_name not in PACKAGE_PRICES:
        messages.error(request, "Invalid package.")
        return redirect("/#packages")
    return redirect("package_payment", package_name=package_name)


@login_required
def book_service(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request."}, status=400)

    service = request.POST.get("service", "").strip()
    booking_date = request.POST.get("booking_date", "").strip()
    booking_time = request.POST.get("booking_time", "").strip()
    address = request.POST.get("address", "").strip()
    note = request.POST.get("note", "").strip()

    allowed_services = {choice[0] for choice in ServiceBooking.SERVICE_CHOICES}
    if service not in allowed_services:
        return JsonResponse({"success": False, "message": "Please select a valid service."}, status=400)
    if not booking_date or not booking_time or not address:
        return JsonResponse({"success": False, "message": "Please fill all required booking details."}, status=400)

    try:
        parsed_date = date.fromisoformat(booking_date)
    except ValueError:
        return JsonResponse({"success": False, "message": "Invalid booking date."}, status=400)
    if parsed_date < timezone.localdate():
        return JsonResponse({"success": False, "message": "Please choose a future date."}, status=400)

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    mother, _ = MotherProfile.objects.update_or_create(
        email=request.user.email,
        defaults={
            "name": request.user.first_name or request.user.username,
            "phone": profile.phone,
        },
    )

    booking = ServiceBooking.objects.create(
        mother=mother,
        service=service,
        booking_date=parsed_date,
        booking_time=booking_time,
        address=address,
        note=note,
    )
    create_notification(
        request.user,
        "Booking received",
        f"Your {booking.service} request #{booking.id} is pending confirmation.",
    )
    return JsonResponse({
        "success": True,
        "message": "Booking request received successfully.",
        "booking_id": booking.id,
    })


@login_required
def emergency_request(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request."}, status=400)

    latitude = request.POST.get("latitude", "").strip()
    longitude = request.POST.get("longitude", "").strip()
    if not latitude or not longitude:
        return JsonResponse({"success": False, "message": "Location permission is required for emergency support."}, status=400)

    emergency = EmergencyRequest.objects.create(
        user=request.user,
        latitude=latitude,
        longitude=longitude,
        status="Pending",
    )
    create_notification(
        request.user,
        "Emergency request received",
        f"Emergency request #{emergency.id} has been received. A support team can review it from the operations dashboard.",
    )
    return JsonResponse({
        "success": True,
        "message": "Emergency request received.",
        "request_id": emergency.id,
        "status": emergency.status,
    })


@login_required
def create_package_payment(request, package_name):
    if package_name not in PACKAGE_PRICES:
        return JsonResponse({"success": False, "message": "Invalid package."}, status=400)

    amount = PACKAGE_PRICES[package_name]
    if request.method == "POST":
        payment = PaymentRecord.objects.create(
            user=request.user,
            package=package_name,
            amount=amount,
            status="Pending",
        )
        create_notification(
            request.user,
            "Package selected",
            f"{package_name} has been selected. Payment record #{payment.id} is pending.",
        )
        messages.success(request, f"{package_name} selected. Payment is pending.")
        return redirect("/#profile")

    return render(request, "package_payment.html", {"package": package_name, "amount": amount})


@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.read = True
    notification.save(update_fields=["read"])
    return JsonResponse({"success": True})


@login_required
def submit_review(request, booking_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request."}, status=400)

    booking = get_object_or_404(ServiceBooking, id=booking_id, mother__email=request.user.email)
    if booking.status != "Completed":
        return JsonResponse({"success": False, "message": "You can review a service after it is completed."}, status=400)
    if hasattr(booking, "review"):
        return JsonResponse({"success": False, "message": "This booking has already been reviewed."}, status=400)

    try:
        rating = int(request.POST.get("rating", "0"))
    except ValueError:
        rating = 0
    comment = request.POST.get("comment", "").strip()
    if rating not in range(1, 6):
        return JsonResponse({"success": False, "message": "Rating must be between 1 and 5."}, status=400)

    Review.objects.create(
        booking=booking,
        user=request.user,
        rating=rating,
        comment=comment,
    )
    create_notification(request.user, "Thank you for your feedback", "Your MotherCare service review was submitted.")
    return JsonResponse({"success": True, "message": "Thank you for your review."})


def provider_user_required(view):
    @login_required
    def wrapped(request, *args, **kwargs):
        try:
            provider = request.user.service_provider
        except ServiceProvider.DoesNotExist:
            return render(request, "provider_dashboard.html", {"access_denied": True})
        if not provider.verified:
            return render(request, "provider_dashboard.html", {"access_denied": True, "provider": provider})
        return view(request, provider, *args, **kwargs)
    return wrapped


@provider_user_required
def provider_dashboard(request, provider):
    bookings = ServiceBooking.objects.filter(assigned_provider=provider).select_related("mother").order_by("booking_date", "booking_time")
    return render(request, "provider_dashboard.html", {"provider": provider, "bookings": bookings})


@provider_user_required
def provider_update_booking(request, provider, booking_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request."}, status=400)
    booking = get_object_or_404(ServiceBooking, id=booking_id, assigned_provider=provider)
    status = request.POST.get("status", "").strip()
    allowed = {"Confirmed", "In Progress", "Completed", "Cancelled"}
    if status not in allowed:
        return JsonResponse({"success": False, "message": "Invalid booking status."}, status=400)
    booking.status = status
    booking.save(update_fields=["status"])
    try:
        customer = User.objects.get(email=booking.mother.email)
        create_notification(customer, "Booking updated", f"Booking #{booking.id} is now {status}.")
    except User.DoesNotExist:
        pass
    return JsonResponse({"success": True, "message": f"Booking marked {status}."})


def staff_required(view):
    return user_passes_test(lambda user: user.is_staff, login_url="/admin/login/")(view)


@staff_required
def operations_dashboard(request):
    bookings = ServiceBooking.objects.select_related("mother", "assigned_provider").order_by("-created_at")[:100]
    emergencies = EmergencyRequest.objects.select_related("user").order_by("-created_at")[:100]
    providers = ServiceProvider.objects.order_by("role", "name")
    return render(request, "operations_dashboard.html", {
        "bookings": bookings,
        "emergencies": emergencies,
        "providers": providers,
    })


@staff_required
def operations_assign_provider(request, booking_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request."}, status=400)
    booking = get_object_or_404(ServiceBooking, id=booking_id)
    provider_id = request.POST.get("provider_id", "")
    provider = get_object_or_404(ServiceProvider, id=provider_id, verified=True, available=True)
    booking.assigned_provider = provider
    booking.status = "Confirmed"
    booking.save(update_fields=["assigned_provider", "status"])
    try:
        customer = User.objects.get(email=booking.mother.email)
        create_notification(customer, "Provider assigned", f"{provider.name} has been assigned to booking #{booking.id}.")
    except User.DoesNotExist:
        pass
    if provider.user_id:
        create_notification(provider.user, "New booking assigned", f"Booking #{booking.id} has been assigned to you.")
    return JsonResponse({"success": True, "message": "Provider assigned successfully."})


def privacy_policy(request):
    return render(request, "privacy.html")


def terms_conditions(request):
    return render(request, "terms.html")
