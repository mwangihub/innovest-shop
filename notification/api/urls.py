from django.urls import path, include
from .views import NotificationAPIView, NotificationUpdateAPIView

urlpatterns = [
    path("get-for-user/", NotificationAPIView.as_view(), name="get_for_user"),
    path("remove-for-user/", NotificationAPIView.as_view(), name="remove_for_user"),
    path("mark-all-for-user/", NotificationUpdateAPIView.as_view(), name="mark_all_for_user"),
]
