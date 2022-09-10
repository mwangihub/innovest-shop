
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
    path("", ShopTemplateView.as_view(), name="shop"),
    path('favicon.ico', favicon_view),
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
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [path("db/", admin.site.urls), ]
