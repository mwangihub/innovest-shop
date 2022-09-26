import django
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import render

import core.UrlsViewSiteMap
import shop.sitemaps
from shop.views import ShopTemplateView
from job.views import JobTemplateView
from home.views import HomeTemplateView
from django.urls import path, re_path, include
from django.conf.urls import handler404
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.sitemaps.views import sitemap

sitemaps = {
    "static": core.UrlsViewSiteMap.StaticViewSitemap,
}

urlpatterns = [

    path("auth/", include("user.urls")),
    path("shop/", ShopTemplateView.as_view(), name="shop"),
    path("job/", JobTemplateView.as_view(), name="job"),
    path("", HomeTemplateView.as_view(), name="home"),
    # path("404/", custom_page_not_found),
    # path("500/", custom_server_error),
    path("sitemap.xml", sitemap, {'sitemaps': sitemaps}, name='innovest_sitemap'),
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
        path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicons/favicon.ico'))),
        path("admin/", admin.site.urls),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        path("management/admin/", admin.site.urls),
    ]

handler404 = 'core.views.custom_page_not_found'
# handler500 = 'core.views.custom_server_error'
