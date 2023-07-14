
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin


import core.sitemaps
from shop.views import ShopTemplateView
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.sitemaps.views import sitemap

sitemaps = {
    "static": core.sitemaps.StaticViewSitemap,
}

urlpatterns = [
    path("auth/", include("user.urls")),
    path("", ShopTemplateView.as_view(), name="shop"),
    path("sitemap.xml", sitemap, {'sitemaps': sitemaps}, name='innovest_sitemap'),

    path('api/', include([
        path('auth/', include([
            path('', include("api_auth.urls", )),
            path('', include("api_auth.registration.urls", )),
        ])),
        path('shop/', include("shop.api.urls", )),
        path('notification/', include("notification.api.urls", )),
        path('user/', include("user.api.urls", )),
    ]))
]

if settings.DEBUG:
    urlpatterns += [
        path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicons/favicon.ico'))),
        path("admin/", admin.site.urls),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        path("management/admin/", admin.site.urls),
    ]
