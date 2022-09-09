
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib import auth
from django.conf import settings

from core.methods import send_email

User = auth.get_user_model()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    # For the purpose of using session authentication. To be extended later
    csrfmiddlewaretoken = serializers.CharField(required=False, allow_blank=True)

    def authenticate(self, **kwargs):
        return auth.authenticate(self.context['request'], **kwargs)

    def _validate_email(self, email, password):
        user = None
        if email and password:
            user = self.authenticate(email=email, password=password)
        else:
            raise serializers.ValidationError({"Incorrect": 'Must include "correct email" and "correct password". '
                                                            'Check your credentials and try again.'})
        return user

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = self._validate_email(email, password)
        # Did we get back an active user?
        if user:
            if not user.is_active:
                raise serializers.ValidationError({"Inactive account": 'Activate your Account then login.'})
        else:
            raise serializers.ValidationError({"Credentials": 'Unable to log in with provided credentials.'})
        attrs['user'] = user
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    employee = serializers.BooleanField(required=False, allow_null=True,
                                        help_text="To carry out actions related to job application")
    buyer = serializers.BooleanField(required=False, allow_null=True,
                                     help_text="To carry out actions related to buying items")

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2', "buyer", "employee"]

    def validate(self, attrs):
        """
        The validate function is called when the serializer is passed a dictionary of data. 
        It validates that all required fields are present and that no extra fields are included. 
        If validation passes, it returns the validated data as a dictionary; otherwise, it raises an exception.
        
        :param self: Reference the class itself
        :param attrs: Pass the validated data
        :return: A dictionary with the key 'password2' and a value of none
        """
        error_obj = {}
        if attrs['password1'] != attrs['password2']:
            error_obj["Password"] = "Password fields didn't match."
        try:
            user = User.objects.get_user_by_email(attrs['email'])
            if user:
                error_obj["Email"] = "User with this email exists. Try restting password/contact us."
        except User.DoesNotExist:
            pass
        if len(error_obj) > 0:
            raise serializers.ValidationError(error_obj)
        return attrs

    def create(self, validated_data):
        """
        The create function creates a new user object and saves it to the database.
        It also sets the password correctly and marks it as active. If ACCOUNT_AUTO_LOGIN_ON_SIGNUP is set, 
        it automatically logs in the user after creating their account.
        
        :param self: Reference the class instance itself
        :param validated_data: Pass in the dictionary of validated data from our serializer
        :return: The user object that was created
        """
        # ACCOUNT_VERIFIED_ON_SIGNUP
        request = self.context.get("request")
        user = User.objects.create(email=validated_data['email'])
        user.set_password(validated_data['password1'])
        if validated_data['employee']:
            user.employee = True
            user.non = False
        if validated_data['buyer']:
            user.buyer = True
            user.non = False
        # TODO: confingure google developer console to send email
        # if settings.ACCOUNT_VERIFIED_ON_SIGNUP:
        #     send_email('Please, activate your account.', recipients=[email],
        #                html_and_context= {
        #                    "template_name": "account/verification_sent.html",
        #                    "context": {}
        #                })
        user.is_active = True
        user.save()
        if settings.ACCOUNT_AUTO_LOGIN_ON_SIGNUP:
            self.perform_authentication(request, validated_data)
        return user

    def perform_authentication(self, request, data, *args, **kwargs):
        """
        The perform_authentication function is used to authenticate the user. It takes in a request and data as arguments, 
        and returns a new_user object if the authentication is successful. If not, it returns None.
        
        :param self: Access variables that belongs to the class
        :param request: Get the user object
        :param data: Pass the data from the serializer to the authenticate function
        :param *args: Pass a variable number of arguments to a function
        :param **kwargs: Pass additional keyword arguments when the function is called
        :return: The user object
        """
        new_user = auth.authenticate(email=data['email'], password=data['password1'])
        if new_user is not None:
            auth.login(request, new_user)
