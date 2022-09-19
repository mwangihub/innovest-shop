from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponse

# Create your views here.
from core.methods import app_active_check


class ShopTemplateView(TemplateView):
    template_name = 'shop/index.html'
    app_name = None

    def get(self, request, *args, **kwargs) -> HttpResponse:
        self.app_name = self.request.resolver_match.url_name
        active = app_active_check(self.app_name)
        if active:
            return redirect("/")
        domain = f"{request.scheme}://{request.get_host()}/"
        context = {
            'title': "welcome to Innovest shop",
            'domain': domain
        }
        return render(request, self.template_name, context)
