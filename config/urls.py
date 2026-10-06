from django.contrib import admin
from django.urls import path

from care.views import (
    home,
    register,
    login_user,
    logout_user,
    choose_package,
    book_service,
    emergency_request,
    create_package_payment,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", home, name="home"),

    path("register/", register, name="register"),

    path("login/", login_user, name="login"),

    path("logout/", logout_user, name="logout"),

    path(
        "choose-package/<str:package_name>/",
        choose_package,
        name="choose_package",
    ),

    path(
        "book-service/",
        book_service,
        name="book_service",
    ),

    path(
        "emergency/",
        emergency_request,
        name="emergency_request",
    ),

    path(
        "package-payment/<str:package_name>/",
        create_package_payment,
        name="package_payment",
    ),
]
