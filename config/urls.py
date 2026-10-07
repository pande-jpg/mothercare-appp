from django.contrib import admin
from django.urls import path

from care.views import (
    book_service,
    choose_package,
    create_package_payment,
    emergency_request,
    home,
    login_user,
    logout_user,
    mark_notification_read,
    operations_assign_provider,
    operations_dashboard,
    privacy_policy,
    provider_dashboard,
    provider_update_booking,
    register,
    submit_review,
    terms_conditions,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("choose-package/<str:package_name>/", choose_package, name="choose_package"),
    path("book-service/", book_service, name="book_service"),
    path("emergency/", emergency_request, name="emergency_request"),
    path("package-payment/<str:package_name>/", create_package_payment, name="package_payment"),
    path("privacy/", privacy_policy, name="privacy_policy"),
    path("terms/", terms_conditions, name="terms_conditions"),
    path("notifications/<int:notification_id>/read/", mark_notification_read, name="mark_notification_read"),
    path("booking/<int:booking_id>/review/", submit_review, name="submit_review"),
    path("provider/", provider_dashboard, name="provider_dashboard"),
    path("provider/booking/<int:booking_id>/status/", provider_update_booking, name="provider_update_booking"),
    path("operations/", operations_dashboard, name="operations_dashboard"),
    path("operations/booking/<int:booking_id>/assign/", operations_assign_provider, name="operations_assign_provider"),
]
