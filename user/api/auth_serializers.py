from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib import auth
from django.conf import settings
from user.models import BuyerProfile, InnovestUsersMessages, Project
from core.methods import _user, send_email
from api_auth.serializers import UserDetailsSerializer

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
        error_obj = {}
        if attrs['password1'] != attrs['password2']:
            error_obj["Password"] = "Password fields didn't match."
        try:
            user = User.objects.get_user_by_email(attrs['email'])
            if user:
                error_obj["Email"] = "User with this email exists. Try resting password or contact us."
        except User.DoesNotExist:
            pass
        if len(error_obj) > 0:
            raise serializers.ValidationError(error_obj)
        return attrs

    def create(self, validated_data):
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

        if settings.ACCOUNT_VERIFIED_ON_SIGNUP:
            send_email(
                subject='Please, activate your account.',
                recipients=[validated_data['email'], ],
                from_email=settings.EMAIL_HOST_USER,
                # html_and_content= {"template_name": "account/verification_sent.html","context": {} }
            )
        user.is_active = settings.ACCOUNT_VERIFIED_ON_SIGNUP
        user.save()
        if settings.ACCOUNT_AUTO_LOGIN_ON_SIGNUP:
            self.perform_authentication(request, validated_data)
        return user

    def perform_authentication(self, request, data, *args, **kwargs):
        new_user = auth.authenticate(email=data['email'], password=data['password1'])
        if new_user is not None:
            auth.login(request, new_user)


class BuyerProfileSerializer(serializers.ModelSerializer):
    account = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    avatar = serializers.ImageField(allow_empty_file=True)

    class Meta:
        model = BuyerProfile
        fields = ["account", "avatar", "phone", "address", "gender"]

    def get_account(self, obj):
        user = _user(self.context['request'])
        return UserDetailsSerializer(obj.user).data

    def get_gender(self, obj):
        return obj.get_gender_display()


class InnovestMessagesSerializers(serializers.ModelSerializer):
    """
    Make sure to pass request in context
    """

    class Meta:
        model = InnovestUsersMessages
        fields = ["names", "email", "subject", "message"]

    def validate(self, attrs):
        user = self.context['request'].user
        session_user = user
        if user.is_anonymous:
            req = self.context['request']
            session_user = f"IP: {req.META.get('REMOTE_ADDR')}, Browser: {req.META.get('HTTP_USER_AGENT')}"
        attrs['session_user'] = session_user
        return attrs


class ProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "project_name", "category", "client", "project_url", "alias_name", "mentioned_date", "display", "deployed_url"]
