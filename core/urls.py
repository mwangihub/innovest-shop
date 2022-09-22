from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

import core.UrlsViewSiteMap
import shop.sitemaps
from shop.views import ShopTemplateView
from job.views import JobTemplateView
from home.views import HomeTemplateView
from django.urls import path, re_path, include
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.sitemaps.views import sitemap


class FaviconView(RedirectView):
    permanent = True
    # query_string = True
    pattern_name = 'article-detail'

    def get_redirect_url(self, *args, **kwargs):
        print("redirecting to favicons")
        return super().get_redirect_url(*args, **kwargs)


sitemaps = {
    "static": core.UrlsViewSiteMap.StaticViewSitemap,
}

urlpatterns = [
    # path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('/staticfiles/favicons/favicon.ico'))),
    path("sitemap.xml", sitemap, {'sitemaps': sitemaps}, name='innovest_sitemap'),
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
        path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicons/favicon.ico'))),
        path("admin/", admin.site.urls),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        path("management/admin/", admin.site.urls),
        # path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('staticfiles/favicons/favicon.ico'))),
        # re_path(r'^favicon\.ico$', RedirectView.as_view(url=static('/static/favicon.ico'), permanent=True))
    ]
