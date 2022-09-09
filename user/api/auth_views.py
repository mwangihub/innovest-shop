from importlib import import_module

from django.conf import settings
from django.contrib import auth
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api_auth.serializers import LoginSerializer as DefaultLoginSerializer
from api_auth.serializers import UserDetailsSerializer
from . import auth_serializers as serializers

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


@method_decorator(ensure_csrf_cookie, name="dispatch")
class GetCSRFTOKENView(APIView):
    permission_classes = [permissions.AllowAny, ]

    def get(self, request, *args, **kwargs):
        """
        The get function is used to retrieve a single object from the database. 
        It takes in an id as an argument and returns the corresponding object if it exists, otherwise it returns a 404 error.
        :param self: Access the attributes and methods of the class
        :param request: Access the request object
        :param *args: Pass a variable number of arguments to a function
        :param **kwargs: Pass a variable number of keyword arguments to the view function
        :return: A response object
        """
        if request.user.is_authenticated:
            return Response({'isAuthenticated': True}, status=status.HTTP_200_OK)
        return Response({'isAuthenticated': False}, status=status.HTTP_200_OK)



@method_decorator(csrf_protect, name='dispatch')
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
            profile = UserDetailsSerializer(user, many=False, context={"request": request})
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
        # TODO: Implement Email if ACCOUNT_AUTO_LOGIN_ON_SIGNUP is false;
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

    def get(self, request, *args, **kwargs) -> HttpResponse:
        """
        The get function is used to retrieve a single object. 
        It takes the id of the object as an argument and returns a json representation of that object.
        :param self: Access variables that belongs to the class
        :param request: Get the request object that django has created for your view
        :param *args: Send a non-keyworded variable length argument list to the function
        :param **kwargs: Pass a keyworded, variable-length argument list
        :return: A httpresponse object
        """
        response_obj = {
            'isAuthenticated': request.user.is_authenticated,
            'profile': None
        }
        if request.user.is_authenticated:
            profile = UserDetailsSerializer(request.user, many=False, context={"request": request})
            response_obj['profile'] = profile.data

        return Response(response_obj, status=status.HTTP_200_OK)
