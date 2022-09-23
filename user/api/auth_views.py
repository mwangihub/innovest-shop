from importlib import import_module

from django.conf import settings
from django.contrib import auth
from django.contrib.auth import login
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect, csrf_exempt
from rest_framework import permissions
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from api_auth.serializers import LoginSerializer as DefaultLoginSerializer
from api_auth.serializers import UserDetailsSerializer
from user.api import auth_serializers as serializers
from user.models import BuyerProfile, Project
from core.methods import _user
from django.contrib.sites.shortcuts import get_current_site
from core.methods import send_mass_mail, send_email, get_rendered_html

User = auth.get_user_model()


def import_callable(path_or_callable):
    """
    The import_callable function imports a callable from its fully qualified name.
    Args: path_or_callable (str): The import path of the callable to import, or the callable itself
    Returns: A function that can be called with ``*args`` and ``**kwargs`` arguments.  
    If passed a single argument, it will be interpreted as ``*args``.
    :param path_or_callable: Specify either a callable or a string
    :return: The callable objec
    """
    if hasattr(path_or_callable, '__call__'):
        return path_or_callable
    else:
        assert isinstance(path_or_callable, str)
        package, attribute = path_or_callable.rsplit('.', 1)
        return getattr(import_module(package), attribute)


settings_serializers = getattr(settings, 'REST_AUTH_SERIALIZERS', {})
LoginSerializer = import_callable(settings_serializers.get('LOGIN_SERIALIZER', DefaultLoginSerializer))


def is_authenticated_response(request, profile, extra=None, stat=None, *args, **kwargs):
    return Response({
        "profile": profile.data,
        "details": "authentication successful",
        "isAuthenticated": request.user.is_authenticated,
        "success": True,
        "extra": extra
    }, status=stat)


class ProjectsMetaData(APIView):
    serializer_class = serializers.ProjectsSerializer
    permission_classes = [permissions.AllowAny, ]

    def post(self, format=None, *args, **kwargs):
        qs = Project.objects.all()
        print(qs)
        serializer = self.serializer_class(qs, many=True, context={'request': self.request})
        return Response({"projects": serializer.data}, status=status.HTTP_200_OK)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class GetCSRFTOKENView(APIView):
    permission_classes = [permissions.AllowAny, ]

    def get(self, *args, **kwargs):
        from django.middleware.csrf import get_token
        csrf_token = get_token(self.request)
        return Response(
            {'isAuthenticated': self.request.user.is_authenticated,
             "csrf_token": csrf_token
             }, status=status.HTTP_200_OK)


# @method_decorator(csrf_protect, name='dispatch')
class LoginView(APIView):
    permission_classes = [permissions.AllowAny, ]
    serializer_class = serializers.LoginSerializer

    def post(self, request, *args, **kwargs):
        email = request.data['email']
        password = request.data['password']
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid():
            user = auth.authenticate(email=email, password=password)
            auth.login(request, user)
            qs, created = BuyerProfile.objects.get_or_create(user=user)
            profile = serializers.BuyerProfileSerializer(instance=qs, many=False, context={"request": request})
            return Response({
                "profile": profile.data,
                "details": "Authentication successful",
                "isAuthenticated": request.user.is_authenticated,
                "success": True,
                "extra": {}
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "profile": None,
                "details": {"info": serializer.errors},
                "isAuthenticated": False,
                "success": False,
                "extra": {}
            },
                status=status.HTTP_200_OK)


@method_decorator(csrf_protect, name='dispatch')
class SignUpView(APIView):
    """
        The SignUpView creates a new user and returns the serialized data of that user
        - Change ACCOUNT_AUTO_LOGIN_ON_SIGNUP to false to skip auto signup
        - TODO: This view has not implemented email verification
        :param self: Access the class that is being created
        :param request: Get the user object
        :param *args: Send a non-keyworded variable length argument list to the function
        :param **kwargs: Pass in a variable number of keyword arguments to the function
        :return: A response_data object
        """
    queryset = User.objects.all()
    serializer_class = serializers.RegisterSerializer
    permission_classes = [permissions.AllowAny, ]
    validation_serializer = None

    def post(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            if settings.ACCOUNT_AUTO_LOGIN_ON_SIGNUP:
                user = request.user
                profile = UserDetailsSerializer(user, many=False, context={"request": request})
                # return is_authenticated_response(request, profile, serializer.data, status.HTTP_201_CREATED)
                return Response({
                    "profile": profile.data,
                    "details": "Successfully registered.",
                    "isAuthenticated": request.user.is_authenticated,
                    "success": True,
                    "extra": serializer.data
                }, status=status.HTTP_201_CREATED)
        return Response({
            "profile": None,
            "details": {"info": serializer.errors},
            "isAuthenticated": False,
            "success": False,
            "extra": {}
        },
            status=status.HTTP_200_OK)


class LogOutView(APIView):
    permission_classes = [permissions.AllowAny, ]

    def post(self, request, *args, **kwargs) -> HttpResponse:
        """
          The post function logs out the user and returns a response with a success message.
          :param self: Access the class that is calling it
          :param request: Get the current request object
          :param *args: Pass a variable number of arguments to a function
          :param **kwargs: Pass a variable number of keyword arguments to a function
          :return: An httpresponse with a status code of 200
          """
        auth.logout(request)
        return Response({
            "detail": _("Successfully logged out."),
            'isAuthenticated': request.user.is_authenticated
        }, status=status.HTTP_200_OK)


class CheckAuth(APIView):
    permission_classes = [permissions.AllowAny, ]
    serializer_class = serializers.BuyerProfileSerializer

    def get(self, request, *args, **kwargs) -> HttpResponse:
        response_obj = {
            'isAuthenticated': request.user.is_authenticated,
            'profile': None
        }
        qs, created = BuyerProfile.objects.get_or_create(user=_user(request))
        profile = self.serializer_class(instance=qs, many=False, context={"request": self.request})
        response_obj['profile'] = profile.data
        if settings.DEV_MODE:
            response_obj['isAuthenticated'] = True
        return Response(response_obj, status=status.HTTP_200_OK)


# @method_decorator(csrf_exempt, name='dispatch')
class RetrieveBuyerProfileView(APIView):
    permission_classes = [permissions.AllowAny, ]
    serializer_class = serializers.BuyerProfileSerializer
    parser_class = (MultiPartParser,)

    def get(self, format=None, *args, **kwargs) -> HttpResponse:
        user = _user(self.request)
        qs, created = BuyerProfile.objects.get_or_create(user=user)
        profile = self.serializer_class(instance=qs, many=False, context={"request": self.request})
        return Response({
            "buyer_profile": profile.data
        }, status=status.HTTP_200_OK)

    def post(self, *args, **kwargs) -> HttpResponse:
        user = _user(self.request)
        user_ = user
        full_names = self.request.data.get('full_name', None)
        if full_names:
            user_serializer = UserDetailsSerializer(instance=user, data={
                "first_name": full_names.split()[0],
                "last_name": full_names.split()[1]
            }, partial=True, context={"request": self.request})
            if user_serializer.is_valid():
                user_ = user_serializer.save()
        qs, created = BuyerProfile.objects.get_or_create(user=user_)
        qs.address = self.request.data.get('address', qs.address)
        qs.phone = self.request.data.get('phone', qs.phone)
        qs.avatar = self.request.data.get('avatar', qs.avatar)
        qs.gender = self.request.data.get('gender', qs.gender)
        qs.user = user
        profile_update = qs.save()
        serializer = self.serializer_class(instance=profile_update, many=False, context={"request": self.request})
        return Response({
            "details": "Successfully updated profile.",
            'updated': True,
            "data": serializer.data
        }, status=status.HTTP_200_OK)


# @method_decorator(csrf_exempt, name='dispatch')
class ChangePasswordAuthUserView(APIView):
    permission_classes = [permissions.AllowAny, ]

    def post(self, *args, **kwargs):
        user = _user(self.request)
        data = self.request.data
        password = data["password"]
        new_password = data["newpassword"]
        re_new_password = data["renewpassword"]
        user = auth.authenticate(email=user.email, password=password)
        if not user:
            return Response({"passwordError": 'Your CURRENT password is not correct.'}, status=status.HTTP_200_OK)
        if not new_password == re_new_password:
            return Response({"passwordError": 'New password and confirmation must match'}, status=status.HTTP_200_OK)
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response({"passwordError": f'{e}'}, status=status.HTTP_200_OK)
        user.set_password(new_password)
        user.save()
        authenticated_user = auth.authenticate(username=user.username, password=new_password)
        auth.login(self.request, authenticated_user)
        return Response({
            "passwordSuccess": "Password successfully updated"
        }, status=status.HTTP_200_OK)


# @method_decorator(csrf_exempt, name='dispatch')
class InnovestUsersMessagesView(APIView):
    permission_classes = [permissions.AllowAny, ]
    serializer_class = serializers.InnovestMessagesSerializers

    def send_mail_(self):
        html_content = get_rendered_html("email/pminnovest/message.html", {"msg": self.request.data})
        subject = self.request.data.get('subject', None)
        email = self.request.data.get('email', None)
        send_email(
            subject=email,
            html_content=html_content,
            from_email=settings.EMAIL_HOST_USER,
            recipients=["pminnovest@gmail.com", ],
        )

    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data, context={'request': self.request})
        self.send_mail_()
        if serializer.is_valid():
            # serializer.save()
            return Response({
                'success': "Your message have been received. Thank you."
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': "There was an error sending your message",
                             'data': serializer.errors
                             }, status=status.HTTP_200_OK)
