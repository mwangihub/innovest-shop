from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site


# Create your views here.
class HomeTemplateView(TemplateView):
    template_name = 'home/index.html'

    def get(self, request, *args, **kwargs) -> HttpResponse:
        domain = f"{request.scheme}://{request.get_host()}/"
        context = {
            'title': "Innovest | pminnovest.com",
            'domain': domain
        }
        return render(request, self.template_name, context)
