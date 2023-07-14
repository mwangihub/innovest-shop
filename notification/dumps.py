# def notify_user(self, user: object, title: str, message: str = None, level: str = 'info', icon: str = None) -> object:
#     """Sends a new notification to user. Returns newly created notification object.
#     """
#     max_notifications = 30
#     if user:
#         max_notifications = self._max_notifications_per_user()
#     if user:
#         if self.filter(user=user).count() >= max_notifications:
#             to_be_deleted_qs = self.filter(user=user).order_by("-timestamp")[max_notifications - 1:]
#             for notification in to_be_deleted_qs:
#                 notification.delete()
#     if not message:
#         message = title
#
#     if level not in self.model.Level:
#         level = self.model.Level.INFO
#     obj_to_create = {
#         'title': title,
#         'message': message,
#         'level': level,
#         'icon': icon
#     }
#     if user:
#         obj_to_create['user'] = user
#         obj = self.create(**obj_to_create)
#         return model_to_dict(obj)
#     return obj_to_create
#
# def _max_notifications_per_user(self) -> int:
#     """Maximum number of notifications allowed per user."""
#     max_notifications = getattr(
#         settings,
#         "NOTIFICATIONS_MAX_PER_USER",
#         self.model.NOTIFICATIONS_MAX_PER_USER_DEFAULT
#     )
#     try:
#         max_notifications = int(max_notifications)
#     except ValueError:
#         max_notifications = None
#     if max_notifications is None or max_notifications < 0:
#         max_notifications = self.model.NOTIFICATIONS_MAX_PER_USER_DEFAULT
#     return max_notifications
#
# def user_unread_count(self, user_pk: int) -> int:
#     """
#         Returns the cached unread count for a user given by user PK
#         Will return -1 if user can not be found
#     """
#     cache_key = self._user_notification_cache_key(user_pk)
#     unread_count = cache.get(key=cache_key)
#     if not unread_count:
#         try:
#             user = User.objects.get(pk=user_pk)
#         except User.DoesNotExist:
#             unread_count = -1
#         else:
#             unread_count = user.notification_set.filter(viewed=False).count()
#             cache.set(
#                 key=cache_key,
#                 value=unread_count,
#                 timeout=self.USER_NOTIFICATION_COUNT_CACHE_DURATION
#             )
#     else:
#         pass
#     return unread_count
#
# @classmethod
# def invalidate_user_notification_cache(cls, user_pk: int) -> None:
#     cache.delete(key=cls._user_notification_cache_key(user_pk))
#
# @classmethod
# def _user_notification_cache_key(cls, user_pk: int) -> str:
#     return f'{cls.USER_NOTIFICATION_COUNT_PREFIX}_{user_pk}'
# def update(self, *args, **kwargs):
#     """Override update to ensure cache is invalidated on very call."""
#     super().update(*args, **kwargs)
#     user_pks = set(self.select_related("user").values_list('user__pk', flat=True))
#     for user_pk in user_pks:
#         NotificationManager.invalidate_user_notification_cache(user_pk)
