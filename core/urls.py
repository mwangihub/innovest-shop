"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from shop.views import ShopTemplateView

from django.urls import path, include
from django.views.generic.base import RedirectView

from django.contrib.staticfiles.storage import staticfiles_storage


favicon_view = RedirectView.as_view(url=staticfiles_storage.url('favicons/dev_1.jpg'))
urlpatterns = [
    path("auth/", include("user.urls")),
    
    # For API_ENDPOINTS
    path('api/', include([
        path('auth/', include([
            path('', include("api_auth.urls", )),
            path('', include("api_auth.registration.urls", )),
        ])),
        path('shop/', include("shop.api.urls", )),
        path('user/', include("user.api.urls", )),
    ]))
]

if settings.DEBUG:
    urlpatterns += [
        path('favicon.ico', favicon_view),
        path("admin/", admin.site.urls),
        path("", ShopTemplateView.as_view(), name="shop")
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [path("db/", admin.site.urls), ]
