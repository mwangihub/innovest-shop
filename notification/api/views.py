from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from core.methods import _user
from notification.api.serializers import (NotificationSerializer, )
from notification.models import Notification

User = get_user_model()


def update_instance(instance, user):
    """To avoid repetition"""
    instance.users.remove(user)
    instance.user = None
    instance.save()


@method_decorator(csrf_exempt, name="dispatch")
class NotificationAPIView(APIView):
    """
    A view that returns a list of all Notifications related to the user &
    Deletes all Notifications for a specific user
    """
    permission_classes = [permissions.AllowAny, ]
    serializer_class = NotificationSerializer

    def get(self, *args, **kwargs):
        user = _user(self.request)
        qs = None
        if user.is_authenticated:
            qs = Notification.objects.get_for_user(user)
        serializer = self.serializer_class(qs, many=True, context={"request": self.request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, *args, **kwargs):
        """
        To handle Delete only
        TODO:To improve later
        """
        user = _user(self.request)
        remove_all = self.request.data.get('remove_all', None)
        if remove_all:
            for notification in Notification.objects.all():
                update_instance(notification, user)
            return Response({}, status=status.HTTP_200_OK)
        id = self.request.data.get('id', None)
        notification = get_object_or_404(Notification, id=id)
        update_instance(notification, user)
        return Response({}, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class NotificationUpdateAPIView(APIView):
    """
    A view that returns marks viewed_by related to the user.
    """
    permission_classes = [permissions.AllowAny, ]
    serializer_class = NotificationSerializer

    def post(self, *args, **kwargs):
        user = _user(self.request)
        mark_viewed_all = self.request.data.get('mark_viewed_all', None)
        if mark_viewed_all:
            for notification in Notification.objects.all().exclude(viewed_by=user).prefetch_related("viewed_by"):
                notification.mark_viewed_by(user)
            return Response({}, status=status.HTTP_200_OK)
        id = self.request.data.get('id', None)
        notification = get_object_or_404(Notification, id=id)
        notification.mark_viewed(user)
        return Response({}, status=status.HTTP_200_OK)
