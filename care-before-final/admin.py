from django.contrib import admin
from django.utils.html import format_html

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


@admin.register(ServiceBooking)
class ServiceBookingAdmin(admin.ModelAdmin):
    list_display = ("id", "mother", "service", "assigned_provider", "booking_date", "booking_time", "status", "created_at")
    list_filter = ("service", "status", "booking_date", "assigned_provider")
    search_fields = ("mother__name", "mother__email", "mother__phone", "address")
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
    list_display = ("id", "user", "status", "location_link", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email")
    ordering = ("-created_at",)
    actions = ["mark_processing", "mark_resolved"]

    def location_link(self, obj):
        if obj.latitude and obj.longitude:
            url = f"https://www.google.com/maps/search/?api=1&query={obj.latitude},{obj.longitude}"
            return format_html('<a href="{}" target="_blank" rel="noopener">📍 Open Location</a>', url)
        return "No location"

    location_link.short_description = "Location"

    @admin.action(description="Mark emergencies as Processing")
    def mark_processing(self, request, queryset):
        queryset.update(status="Processing")

    @admin.action(description="Mark emergencies as Resolved")
    def mark_resolved(self, request, queryset):
        queryset.update(status="Resolved")


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "user", "phone", "verified", "available", "service_area")
    list_filter = ("role", "verified", "available")
    search_fields = ("name", "phone", "email", "service_area", "user__email")
    list_select_related = ("user",)
    actions = ["verify_providers", "activate_providers"]

    @admin.action(description="Verify selected providers")
    def verify_providers(self, request, queryset):
        queryset.update(verified=True)

    @admin.action(description="Mark providers available")
    def activate_providers(self, request, queryset):
        queryset.update(available=True)


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "package", "amount", "status", "payment_reference", "created_at")
    list_filter = ("status", "package")
    search_fields = ("user__email", "payment_reference")
    ordering = ("-created_at",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "booking", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("user__email", "comment")
    readonly_fields = ("created_at",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "read", "created_at")
    list_filter = ("read", "created_at")
    search_fields = ("user__email", "title", "message")


admin.site.register(MotherProfile)
admin.site.register(UserProfile)
