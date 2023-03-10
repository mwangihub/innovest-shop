import logging

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from django.forms import model_to_dict

logger = logging.getLogger(__name__)


class NotificationQuerySet(models.QuerySet):
    """Custom QuerySet for Notification model"""

    def update(self, *args, **kwargs):
        """Override update to ensure cache is invalidated on very call."""
        super().update(*args, **kwargs)
        user_pks = set(self.select_related("user").values_list('user__pk', flat=True))
        for user_pk in user_pks:
            NotificationManager.invalidate_user_notification_cache(user_pk)


class NotificationManager(models.Manager):
    USER_NOTIFICATION_COUNT_PREFIX = 'USER_NOTIFICATION_COUNT'
    USER_NOTIFICATION_COUNT_CACHE_DURATION = 86_400

    def get_queryset(self):
        return NotificationQuerySet(self.model, using=self._db)

    def for_user_or_general(self, user):
        if user.is_authenticated:
            return self.filter(Q(user=user) | Q(is_general=True))
        else:
            return self.filter(is_general=True)

    def notify_user(self, user: object, title: str, message: str = None, level: str = 'info', icon: str = None) -> object:
        """Sends a new notification to user. Returns newly created notification object.
        """
        max_notifications = 30
        if user:
            max_notifications = self._max_notifications_per_user()
        if user:
            if self.filter(user=user).count() >= max_notifications:
                to_be_deleted_qs = self.filter(user=user).order_by("-timestamp")[max_notifications - 1:]
                for notification in to_be_deleted_qs:
                    notification.delete()
        if not message:
            message = title

        if level not in self.model.Level:
            level = self.model.Level.INFO
        obj_to_create = {
            'title': title,
            'message': message,
            'level': level,
            'icon': icon
        }
        if user:
            obj_to_create['user'] = user
            obj = self.create(**obj_to_create)
            logger.info("Created notification %s", obj)
            return model_to_dict(obj)
        return obj_to_create

    def _max_notifications_per_user(self) -> int:
        """Maximum number of notifications allowed per user."""
        max_notifications = getattr(
            settings,
            "NOTIFICATIONS_MAX_PER_USER",
            self.model.NOTIFICATIONS_MAX_PER_USER_DEFAULT
        )
        try:
            max_notifications = int(max_notifications)
        except ValueError:
            max_notifications = None
        if max_notifications is None or max_notifications < 0:
            logger.warning(
                "NOTIFICATIONS_MAX_PER_USER setting is invalid. Using default."
            )
            max_notifications = self.model.NOTIFICATIONS_MAX_PER_USER_DEFAULT
        return max_notifications

    def user_unread_count(self, user_pk: int) -> int:
        """
            Returns the cached unread count for a user given by user PK
            Will return -1 if user can not be found
        """
        cache_key = self._user_notification_cache_key(user_pk)
        unread_count = cache.get(key=cache_key)
        if not unread_count:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                unread_count = -1
            else:
                logger.debug(
                    'Updating notification cache for user with pk %s', user_pk
                )
                unread_count = user.notification_set.filter(viewed=False).count()
                cache.set(
                    key=cache_key,
                    value=unread_count,
                    timeout=self.USER_NOTIFICATION_COUNT_CACHE_DURATION
                )
        else:
            logger.debug(
                'Returning notification count from cache for user with pk %s', user_pk
            )

        return unread_count

    @classmethod
    def invalidate_user_notification_cache(cls, user_pk: int) -> None:
        cache.delete(key=cls._user_notification_cache_key(user_pk))
        logger.debug('Invalided notification cache for user with pk %s', user_pk)

    @classmethod
    def _user_notification_cache_key(cls, user_pk: int) -> str:
        return f'{cls.USER_NOTIFICATION_COUNT_PREFIX}_{user_pk}'


class ItemManager(models.Manager):
    def already_taken(self):
        qs = self.get_queryset().filter(taken=True)
        return qs

    def by_slug(self, slug):
        qs = self.get_queryset().get(slug=slug)
        return qs

    def not_applied(self, user):
        ids = []
        for applied_job in user.jobsapplication_set.all():
            for job in self.not_taken():
                if job == applied_job.job:
                    ids.append(job.id)
        qs = self.get_queryset().exclude(id__in=ids)
        return qs

    def not_taken(self):
        qs = self.get_queryset().filter(taken=False)
        return qs

    def not_expired(self):
        qs = self.get_queryset().filter(expired=False)
        return qs

    def by_user(self, user):
        qs = self.get_queryset().filter(user=user)
        return qs


class OrderQuerySet(models.QuerySet):
    def not_ordered(self):
        return self.filter(ordered=False)

    def completed_by_user(self, user):
        return self.filter(ordered=True, user=user)


class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)

    def not_ordered(self):
        return self.get_queryset().not_ordered()

    def completed_by_user(self, user):
        return self.get_queryset().completed_by_user(user)


class AddressQuerySet(models.QuerySet):
    def by_user(self, user):
        return self.filter(user=user)


class AddressManager(models.Manager):
    def get_queryset(self):
        return AddressQuerySet(self.model, using=self._db)

    def by_user(self, user):
        return self.get_queryset().by_user(user)


class ShippingLocationChargesManger(models.Manager):
    def by_town(self, town):
        return self.get_queryset().filter(town__name=town)
