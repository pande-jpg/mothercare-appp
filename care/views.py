from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import (
    UserProfile,
    MotherProfile,
    ServiceBooking,
    EmergencyRequest,
)


def home(request):
    profile = None
    bookings = []

    if request.user.is_authenticated:
        profile, created = UserProfile.objects.get_or_create(
            user=request.user
        )

        try:
            mother = MotherProfile.objects.get(
                email=request.user.email
            )
            bookings = ServiceBooking.objects.filter(
                mother=mother
            ).select_related(
                "assigned_provider"
            ).order_by("-created_at")
        except MotherProfile.DoesNotExist:
            bookings = []

    return render(
        request,
        "home.html",
        {
            "user": request.user,
            "profile": profile,
            "bookings": bookings,
        }
    )

def register(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")

        if User.objects.filter(username=email).exists():
            messages.error(
                request,
                "An account with this email already exists."
            )
            return redirect("/#register")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name,
        )

        UserProfile.objects.create(
            user=user,
            phone=phone,
        )

        messages.success(
            request,
            "Account created successfully."
        )

        return redirect("/#profile")

    return redirect("/#register")


def login_user(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=email,
            password=password,
        )

        if user is not None:
            login(request, user)

            messages.success(
                request,
                "Welcome back to MotherCare!"
            )

            return redirect("/#dashboard")

        messages.error(
            request,
            "Invalid email or password."
        )

        return redirect("/#account")

    return redirect("/")


def logout_user(request):
    logout(request)
    return redirect("/")


def choose_package(request, package_name):
    if not request.user.is_authenticated:
        return redirect("/#account")

    profile, created = UserProfile.objects.get_or_create(
        user=request.user
    )

    profile.package = package_name
    profile.save()

    messages.success(
        request,
        "Your MotherCare package has been selected."
    )

    return redirect("/#profile")


def book_service(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {
                "success": False,
                "message": "Please login before booking a service.",
            },
            status=401,
        )

    if request.method == "POST":
        service = request.POST.get("service", "").strip()
        booking_date = request.POST.get(
            "booking_date",
            ""
        ).strip()
        booking_time = request.POST.get(
            "booking_time",
            ""
        ).strip()
        address = request.POST.get(
            "address",
            ""
        ).strip()
        note = request.POST.get(
            "note",
            ""
        ).strip()

        if not service or not booking_date or not booking_time or not address:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Please fill all required booking details.",
                },
                status=400,
            )

        mother, created = MotherProfile.objects.get_or_create(
            email=request.user.email,
            defaults={
                "name": request.user.first_name,
                "phone": request.user.profile.phone,
            },
        )

        ServiceBooking.objects.create(
            mother=mother,
            service=service,
            booking_date=booking_date,
            booking_time=booking_time,
            address=address,
            note=note,
        )

        return JsonResponse(
            {
                "success": True,
                "message": "Booking request received successfully.",
            }
        )

    return JsonResponse(
        {
            "success": False,
            "message": "Invalid request.",
        },
        status=400,
    )


def emergency_request(request):
    if not request.user.is_authenticated:
        return JsonResponse({
            "success": False,
            "message": "Please login before using emergency support."
        }, status=401)

    if request.method == "POST":
        latitude = request.POST.get("latitude", "").strip()
        longitude = request.POST.get("longitude", "").strip()

        emergency = EmergencyRequest.objects.create(
            user=request.user,
            latitude=latitude,
            longitude=longitude,
            status="Pending"
        )

        return JsonResponse({
            "success": True,
            "message": "Emergency request received.",
            "request_id": emergency.id,
            "status": emergency.status
        })

    return JsonResponse({
        "success": False,
        "message": "Invalid request."
    }, status=400)

PACKAGE_PRICES = {
    "Basic Care": 16000,
    "MotherCare Plus": 24000,
    "Premium Care": 35000,
}


def create_package_payment(request, package_name):
    if not request.user.is_authenticated:
        return redirect("/#account")

    from .models import PaymentRecord

    if package_name not in PACKAGE_PRICES:
        return JsonResponse({
            "success": False,
            "message": "Invalid package."
        }, status=400)

    amount = PACKAGE_PRICES[package_name]

    if request.method == "POST":
        payment = PaymentRecord.objects.create(
            user=request.user,
            package=package_name,
            amount=amount,
            status="Pending"
        )

        profile, created = UserProfile.objects.get_or_create(
            user=request.user
        )
        profile.package = package_name
        profile.save()

        messages.success(
            request,
            f"{package_name} selected successfully. Payment is pending."
        )

        return redirect("/#profile")

    return render(request, "package_payment.html", {
        "package": package_name,
        "amount": amount,
    })

def privacy_policy(request):
    return render(request, "privacy.html")

def terms_conditions(request):
    return render(request, "terms.html")
