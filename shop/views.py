from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse


# Create your views here.
class ShopTemplateView(TemplateView):
    template_name = 'shop/index.html'

    def get(self, request, *args, **kwargs) -> HttpResponse:
        """
        The get function is used to return a response to the user. 
        It takes in an HttpRequest object and returns an HttpResponse object.
        :param self: Access the attributes and methods of the class in which it is used
        :param request: Access the request data
        :param *args: Send a non-keyworded variable length argument list to the function
        :param **kwargs: Pass a keyworded, variable-length argument list
        :return: A httpresponse object
        """
        context = {
            'title': "welcome to Innovest shop"
        }
        return render(request, self.template_name, context)
