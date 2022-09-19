import environ
from user.auth_config import *

env = environ.Env(
    DEBUG=(bool, True)
)

BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
SECRET_KEY = env("SECRET_KEY")
DEBUG = env('DEBUG')

DEV_MODE = True
ALLOWED_HOSTS = env("ALLOWED_HOSTS").split(",")
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "django_countries",
    "phonenumber_field",
    'gmailapi_backend',
    'user',
    'shop',
    'job'
]
INSTALLED_APPS += AUTH_INSTALLED_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "corsheaders.middleware.CorsMiddleware",
]
ROOT_URLCONF = 'core.urls'


def debug_folder(x):
    if DEBUG:
        return x
    return ""


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, "web/templates"),
            # For Django css & static
            debug_folder(os.path.join(BASE_DIR, "web/shop"))
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
WSGI_APPLICATION = 'core.wsgi.application'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
if not DEBUG: pass

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'web/static'), ]
# if DEBUG:
#     STATICFILES_DIRS += [BASE_DIR / "web/shop/build"]
STATIC_URL = "static/"
MEDIA_URL = "media/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
MEDIA_ROOT = BASE_DIR / "media"

MIDDLEWARE += CORS_MIDDLEWARE
TEMPLATES[0]["OPTIONS"]["context_processors"] += CONTEXT_PROCESSORS
STATICFILES_DIRS += AUTH_STATIC
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_HOST_USER = "pmwassini@gmail.com"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_HOST = "smtp.gmail.com"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_PORT = 587
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True
ALLOWED_EMAIL = ['wingdevelop@gmail.com', 'demo.mail.wing@gmail.com']
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
]
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
REST_SESSION_LOGIN = True
# CSRF_COOKIE_SAMESITE = 'Strict'
# SESSION_COOKIE_SAMESITE = 'Strict'
# CSRF_COOKIE_HTTPONLY = False  # False since we will grab it via universal-cookies
# SESSION_COOKIE_HTTPONLY = True

# Setting CSRF_COOKIE_SAMESITE and SESSION_COOKIE_SAMESITE to True prevents cookies and CSRF tokens from being sent
# from any external requests. Setting CSRF_COOKIE_HTTPONLY and SESSION_COOKIE_HTTPONLY to True blocks client-side
# JavaScript from accessing the CSRF and session cookies. We set CSRF_COOKIE_HTTPONLY to False since we'll be
# accessing the cookie via JavaScript.

# If you're in production, you should serve your website over HTTPS and enable CSRF_COOKIE_SECURE and
# SESSION_COOKIE_SECURE, which will only allow the cookies to be sent over HTTPS.
CORS_ALLOWED_ORIGINS = ["http://localhost:3000", ]
CORS_ORIGIN_ALLOW_ALL = False
# CORS_ALLOW_HEADERS = ('Access-Control-Allow-Origin',
#                       'Access-Control-Allow-Credentials',
#                       'Authorization', 'Content-Type',
#                       'Cache-Control',
#                       'X-Requested-With',
#                       'x-csrftoken')
# CORS_ALLOW_CREDENTIALS = True
# CSRF_COOKIE_HTTPONLY = False
# SESSION_COOKIE_HTTPONLY = False
# CSRF_USE_SESSIONS = False
# CSRF_COOKIE_SECURE = False
# SESSION_COOKIE_SECURE = False
# SESSION_COOKIE_SAMESITE = 'None'
# CSRF_COOKIE_SAMESITE = 'None'
