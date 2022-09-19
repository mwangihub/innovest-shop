from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
# SOCIAL VIEWS AUTHENTICATION
from allauth.socialaccount.models import SocialApp
# Google login
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api_auth.registration.views import SocialLoginView
from .social_auth_serializers import SocialAppSerializer

from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    # CALLBACK_URL_YOU_SET_ON_GOOGLE
    callback_url = "http://localhost:3000/authentication/signup/"
    client_class = OAuth2Client


# Facebook Login
class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


@method_decorator(csrf_exempt, name='dispatch')
class SocialAppKey(APIView):
    permission_classes = [permissions.AllowAny, ]
    """
    Provide social application keys
    """

    def post(self, format=None, *args, **kwargs):
        name = self.request.data.get("name", None)
        try:
            social_account = SocialApp.objects.get(name=name)
        except SocialApp.DoesNotExist:
            social_account = None
        serializer = SocialAppSerializer(social_account)
        return Response(serializer.data, status=status.HTTP_200_OK)
