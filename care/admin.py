from django.contrib import admin
from django.utils.html import format_html
from .models import MotherProfile, ServiceBooking, UserProfile, EmergencyRequest


@admin.register(ServiceBooking)
class ServiceBookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "mother",
        "service",
        "assigned_provider",
        "booking_date",
        "booking_time",
        "status",
        "created_at",
    )

    list_filter = ("service", "status", "booking_date", "assigned_provider")
    search_fields = (
        "mother__name",
        "mother__email",
        "mother__phone",
        "address",
    )
    ordering = ("-created_at",)

    actions = ["mark_confirmed", "mark_completed", "mark_cancelled"]

    @admin.action(description="Mark selected bookings as Confirmed")
    def mark_confirmed(self, request, queryset):
        queryset.update(status="Confirmed")

    @admin.action(description="Mark selected bookings as Completed")
    def mark_completed(self, request, queryset):
        queryset.update(status="Completed")

    @admin.action(description="Mark selected bookings as Cancelled")
    def mark_cancelled(self, request, queryset):
        queryset.update(status="Cancelled")


@admin.register(EmergencyRequest)
class EmergencyRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "status",
        "location_link",
        "created_at",
    )

    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email")
    ordering = ("-created_at",)

    actions = ["mark_processing", "mark_resolved"]

    def location_link(self, obj):
        if obj.latitude and obj.longitude:
            url = (
                "https://www.google.com/maps/search/?api=1"
                f"&query={obj.latitude},{obj.longitude}"
            )
            return format_html(
                '<a href="{}" target="_blank">📍 Open Location</a>',
                url
            )
        return "No location"

    location_link.short_description = "Location"

    @admin.action(description="Mark emergencies as Processing")
    def mark_processing(self, request, queryset):
        queryset.update(status="Processing")

    @admin.action(description="Mark emergencies as Resolved")
    def mark_resolved(self, request, queryset):
        queryset.update(status="Resolved")


admin.site.register(MotherProfile)
admin.site.register(UserProfile)


from .models import ServiceProvider


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "role",
        "phone",
        "verified",
        "available",
        "service_area",
    )

    list_filter = (
        "role",
        "verified",
        "available",
    )

    search_fields = (
        "name",
        "phone",
        "email",
        "service_area",
    )

    actions = [
        "verify_providers",
        "activate_providers",
    ]

    @admin.action(description="Verify selected providers")
    def verify_providers(self, request, queryset):
        queryset.update(verified=True)

    @admin.action(description="Mark providers available")
    def activate_providers(self, request, queryset):
        queryset.update(available=True)
