from django.urls import path
from . import social_auth_views as social_views
from . import auth_views as auth

urlpatterns = [
    path("google/", social_views.GoogleLogin.as_view(), name="google_rest_login"),
    path("facebook/", social_views.FacebookLogin.as_view(), name="facebook_rest_login"),
    path("social/key", social_views.SocialAppKey.as_view(), name="social_api_keys"),

    path("get-csrf-token/", auth.GetCSRFTOKENView.as_view(), name="get_csrf_token"),
    path("v1/signup/", auth.SignUpView.as_view(), name="user_v1_signup"),
    path("v1/login/", auth.LoginView.as_view(), name="user_v1_login"),
    path("v1/logout/", auth.LogOutView.as_view(), name="user_v1_logout"),
    path("v1/checkauth/", auth.CheckAuth.as_view(), name="user_v1_check_auth"),
    path("v1/buyer-profile/", auth.RetrieveBuyerProfileView.as_view(), name="buyer_v1_profile"),
    path("v1/change-password/auth-user/", auth.ChangePasswordAuthUserView.as_view(), name="change_password_v1_auth-user"),
    path("v1/web-messages/", auth.InnovestUsersMessagesView.as_view(), name="web_v1_messages"),
    path("v1/projects-meta-data/", auth.ProjectsMetaData.as_view(), name="projects_meta_data"),

]
