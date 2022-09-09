from django.urls import path
from . import social_auth_views as social_views
from . import auth_views as auth
urlpatterns = [
    path("ping-me/", social_views.CheckSeverIsOnline.as_view(), name="ping-me"),
    path("google/", social_views.GoogleLogin.as_view(), name="google_rest_login"),
    path("facebook/", social_views.FacebookLogin.as_view(), name="facebook_rest_login"),
    path("social/key/<str:name>/", social_views.SocialAppKey.as_view(), name="social_api_keys"),

    path("get_csrf_token/", auth.GetCSRFTOKENView.as_view(), name="get_csrf_token"),
    path("v1/signup/", auth.SignUpView.as_view(), name="user_v1_signup"),
    path("v1/login/", auth.LoginView.as_view(), name="user_v1_login"),
    path("v1/logout/", auth.LogOutView.as_view(), name="user_v1_logout"),
    path("v1/checkauth/", auth.CheckAuth.as_view(), name="user_v1_checkauth"),
]
