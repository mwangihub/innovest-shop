from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.ShopTemplateView.as_view(), name='shop'),
]
