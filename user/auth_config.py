import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        'rest_framework.permissions.IsAuthenticated',
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # 'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        # 'api_auth.jwt_auth.JWTCookieAuthentication',
    ]
}

AUTH_STATIC = [

]
CONTEXT_PROCESSORS = [
    'django.template.context_processors.request',
]
CORS_MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
]
AUTH_USER_MODEL = "user.User"
AUTHENTICATION_BACKENDS = [
    'allauth.account.auth_backends.AuthenticationBackend',
]
AUTH_INSTALLED_APPS = [
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    # 'allauth.socialaccount.providers.twitter',
    # 'allauth.socialaccount.providers.facebook',
    'api_auth',
    'api_auth.registration',
]
SITE_ID = 1
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile', 'email', 'openid',
            'https://www.googleapis.com/auth/calendar.readonly'
        ]
    }
}
ACCOUNT_ADAPTER = "user.adapter.DefaultAccountAdapter"
# Not needed we will have custom Login & logout views depending on
# website requirements to users i.e different types of users.
# ACCOUNT_SIGNUP_FORM_CLASS = "authentication.forms.RegisterForm"
ACCOUNT_AUTO_LOGIN_ON_SIGNUP = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_VERIFIED_ON_SIGNUP = False
ACCOUNT_EMAIL_VERIFICATION = None
# NB: "mandatory" fails due empty TemplateView were defined just to allow reverse()
# call inside app check: https://github.com/Tivix/django-rest-auth/issues/15
# “mandatory” requires ACCOUNT_EMAIL_REQUIRED = True
# “mandatory” blocks user to logging
# “optional” or “none” to allow logins
# “optional” e-mail verification mail sent
# “none” verification mails are NOT sent.

ACCOUNT_USER_MODEL_EMAIL_FIELD = "email"
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_DISPLAY = lambda user: user.get_short_name()
#     A callable (or string of the form 'some.module.callable_name') that 
#     takes a user as its only argument and returns the display name of the user. 
#     The default implementation returns user.username.

# For the purpose of development, otherwise should be None
#     Controls the life time of the session. Set to None to ask the user
#       (“Remember me?”), False to not remember, and True to always remember.
ACCOUNT_SESSION_REMEMBER = None

ACCOUNT_FORMS = {
    # Check https://django-allauth.readthedocs.io/en/latest/forms.html
    #  for more custom forms
    'login': 'user.forms.CustomAuthForm'
    # 'signup': 'allauth.account.forms.SignupForm',
    # 'add_email': 'allauth.account.forms.AddEmailForm',
    # 'change_password': 'allauth.account.forms.ChangePasswordForm',
    # 'set_password': 'allauth.account.forms.SetPasswordForm',
    # 'reset_password': 'allauth.account.forms.ResetPasswordForm',
    # 'reset_password_from_key': 'allauth.account.forms.ResetPasswordKeyForm',
}
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_VERIFICATION = ACCOUNT_EMAIL_VERIFICATION
SOCIALACCOUNT_FORMS = {
    # 'disconnect': 'allauth.socialaccount.forms.DisconnectForm',
    'signup': 'user.forms.CustomAuthSocialForm',
}
SOCIALACCOUNT_ADAPTER = "user.adapter.CustomSocialAccountAdapter"

# REST_USE_JWT = False
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':
        timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME':
        timedelta(days=30),
    'ROTATE_REFRESH_TOKENS':
        False,
    # True -> to avoid leaks
    'BLACKLIST_AFTER_ROTATION':
        True,
    'UPDATE_LAST_LOGIN':
        False,
    'ALGORITHM':
        'HS256',
    'SIGNING_KEY':
        os.environ.get("SECRET_KEY"),
    'VERIFYING_KEY':
        None,
    'AUDIENCE':
        None,
    'ISSUER':
        None,
    'JWK_URL':
        None,
    'LEEWAY':
        0,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME':
        'HTTP_AUTHORIZATION',
    'USER_ID_FIELD':
        'id',
    'USER_ID_CLAIM':
        'user_id',
    'USER_AUTHENTICATION_RULE':
        'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM':
        'token_type',
    'TOKEN_USER_CLASS':
        'rest_framework_simplejwt.models.TokenUser',
    'JTI_CLAIM':
        'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM':
        'refresh_exp',
    'SLIDING_TOKEN_LIFETIME':
        timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME':
        timedelta(days=1),
}
