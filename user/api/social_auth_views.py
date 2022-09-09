from rest_framework import permissions
# SOCIAL VIEWS AUTHENTICATION
from allauth.socialaccount.models import SocialApp
# Google login
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api_auth.registration.views import SocialLoginView
from .social_auth_serializers import SocialAppSerializer


class CheckSeverIsOnline(APIView):
    def get(self, request, format=None):
        return Response({"online": True}, status=status.HTTP_200_OK)


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    # CALLBACK_URL_YOU_SET_ON_GOOGLE
    callback_url = "http://localhost:3000/authentication/signup/"
    client_class = OAuth2Client


# Facebook Login
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class SocialAppKey(APIView):
    permission_classes = [permissions.AllowAny,]
    """
    Provide social application keys
    """

    def get_object(self, name):
        try:
            return SocialApp.objects.get(name=name)
        except SocialApp.DoesNotExist:
            raise Http404

    def get(self, request, name, format=None):
        social_account = self.get_object(name)
        serializer = SocialAppSerializer(social_account)
        return Response(serializer.data, status=status.HTTP_200_OK)
