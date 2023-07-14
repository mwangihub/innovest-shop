from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q

User = get_user_model()


class NotificationQuerySet(models.QuerySet):
    """Custom QuerySet for Notification model"""


class NotificationManager(models.Manager):

    def get_queryset(self):
        return NotificationQuerySet(self.model, using=self._db)

    def get_for_user(self, user):
        return self.filter(Q(users=user, for_user=False) | Q(user=user, for_user=True)) \
            .prefetch_related('users', 'user').distinct()

    def get_for_all_users(self):
        """If is not authenticated"""
        return None

    def remove_user(self, user):
        return self.users.remove(user)

    def notify(self, title: str, message: str, level: str = 'info', icon: str = "bell-fill", user: object = None, for_user: bool = False) -> object:
        """
        Returns newly created notification object.
        self, title: str, message: str, level: str = 'info', icon: str = "bell-fill", user: object = None, for_user: bool = False
        """
        obj_to_create = {
            'title': title,
            'message': message,
            'level': level,
            'icon': icon,
            'for_user': for_user
        }
        if user:
            obj_to_create['user'] = user
        obj = self.create(**obj_to_create)
        return obj
