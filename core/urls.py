from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

import core.UrlsViewSiteMap
import shop.sitemaps
from shop.views import ShopTemplateView
from job.views import JobTemplateView
from home.views import HomeTemplateView
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.sitemaps.views import sitemap

sitemaps = {
    "static": core.UrlsViewSiteMap.StaticViewSitemap,
}

urlpatterns = [
    path("sitemap.xml", sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path("auth/", include("user.urls")),
    path("shop/", ShopTemplateView.as_view(), name="shop"),
    path("job/", JobTemplateView.as_view(), name="job"),
    path("", HomeTemplateView.as_view(), name="home"),
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
        path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicons/dev_1.jpg'))),
        path("admin/", admin.site.urls),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        path("management/admin/", admin.site.urls),
        path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicons/favicon.ico'))),
    ]
