from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.http import HttpResponse

# Create your views here.
from core.methods import app_active_check
from user.models import DebugFrontEnd


class ShopTemplateView(TemplateView):
    template_name = 'shop/index.html'
    app_name = None

    def get(self, request, *args, **kwargs) -> HttpResponse:
        domain = f"{request.scheme}://{request.get_host()}"
        pathname = request.get_host()
        context = {
            'title': "welcome to Innovest shop",
            'domain': domain,
            'pathname': pathname,
            'scheme': request.scheme,
        }
        return render(request, self.template_name, context)
