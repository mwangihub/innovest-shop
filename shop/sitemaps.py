from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from shop.models import Item


class ItemsSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Item.objects.filter()
