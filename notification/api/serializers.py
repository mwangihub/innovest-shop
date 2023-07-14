from django.db.models import Q
from rest_framework import serializers

from api_auth.serializers import UserDetailsSerializer
from core.methods import _user as get_user
from notification.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    not_viewed_count = serializers.SerializerMethodField()
    is_viewed = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = '__all__'

    def get_not_viewed_count(self, obj):
        """Returns the count of Notifications that user has NOT viewed"""
        request = self.context.get("request", None)
        if not request:
            return None
        user = get_user(request)
        queryset_count = Notification.objects.get_for_user(user).exclude(viewed_by=user).count()
        return queryset_count

    def get_is_viewed(self, obj):
        """Is it viewed by current user"""
        request = self.context.get("request", None)
        if not request:
            return None
        user = get_user(request)
        return obj.is_viewed_by_user(user)

    def get_user(self, obj):
        return UserDetailsSerializer(obj.user).data
