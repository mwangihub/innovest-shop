from django.urls import path, include, re_path
from . import views

urlpatterns = [
    path("accounts/login/", views.account_login_view),
    path("accounts/signup/", views.account_signup_view),
    path("accounts/", include("allauth.urls")),
]
