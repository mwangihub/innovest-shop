from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import (
    CASCADE,
    Model,
    TextChoices,
    CharField,
    TextField,
    DateTimeField,
    BooleanField,
    ManyToManyField,
    ForeignKey
)
from .managers import (NotificationManager, )
from django.utils.translation import gettext_lazy as _

User = get_user_model()


def all_users():
    users = User.objects.all()
    return users


class Notification(Model):
    """Notification to a user within Auth"""

    class Icons(TextChoices):
        """Samples of icons"""
        EXCLAMATION_D_F = 'exclamation-diamond-fill', _('exclamation-diamond-fill')
        EXCLAMATION_D = 'exclamation-diamond', _('exclamation-diamond')
        EXCLAMATION_T_F = 'exclamation-triangle-fill', _('exclamation-triangle-fill')
        EXCLAMATION_T = 'exclamation-triangle', _('exclamation-triangle')
        EXCLAMATION_E_F = 'envelope-exclamation-fill', _('envelope-exclamation-fill')
        EXCLAMATION_E = 'envelope-exclamation', _('envelope-exclamation')
        EXCLAMATION_P = 'person-fill-exclamation', _('person-fill-exclamation')
        EXCLAMATION_P_F = 'person-fill-exclamation-fill', _('person-fill-exclamation-fill')
        EXCLAMATION_DB_F = 'database-fill-exclamation', _('database-fill-exclamation')
        EXCLAMATION_DB = 'database-exclamation', _('database-exclamation')
        ARROW_R = 'arrow-repeat', _('arrow-repeat')
        AWARD_F = 'award-fill', _('award-fill')
        AWARD = 'award', _('award')
        BELL_F = 'bell-fill', _('bell-fill')
        BELL = 'bell', _('bell')
        CART_C_F = 'cart-check-fill', _('cart-check-fill')
        CART_C = 'cart-check', _('cart-check')
        CART_D_F = 'cart-dash-fill', _('cart-dash-fill')
        CART_D = 'cart-dash', _('cart-dash')
        CART_P_F = 'cart-plus-fill', _('cart-plus-fill')
        CART_P = 'cart-plus', _('cart-plus')
        DOWNLOAD = 'download', _('download')
        ENVELOPE_AT_F = 'envelope-at-fill', _('envelope-at-fill')
        ENVELOPE_AT = 'envelope-at', _('envelope-at')
        FILETYPE_XLS = 'filetype-xls', _('filetype-xls')
        FILETYPE_CSV = 'filetype-csv', _('filetype-csv')
        GEO_A_FILL = 'geo-alt-fill', _('geo-alt-fill')
        GEO_A = 'geo-alt', _('geo-alt')

    class Level(TextChoices):
        """A notification level."""

        DANGER = 'danger', _('danger')
        WARNING = 'warning', _('warning')
        INFO = 'info', _('info')
        SUCCESS = 'success', _('success')

        @classmethod
        def from_old_name(cls, name: str) -> object:
            """Map old name to enum. Raises ValueError for invalid names."""
            name_map = {
                "CRITICAL": cls.DANGER,
                "ERROR": cls.DANGER,
                "WARN": cls.WARNING,
                "INFO": cls.INFO,
                "DEBUG": cls.SUCCESS,
            }
            try:
                return name_map[name]
            except KeyError:
                raise ValueError(f"Unknown name: {name}") from None

    # For all users, for_user must be set to False
    users = ManyToManyField(User, blank=True, default=all_users)
    # For single user, and ignore users field in queryset hence for_user must be set to True
    user = ForeignKey(User, on_delete=CASCADE, blank=True, null=True, related_name="notifications")
    level = CharField(choices=Level.choices, max_length=10, blank=True, null=True, default=Level.INFO)
    icon = CharField(choices=Icons.choices, max_length=55, blank=True, null=True, default=Icons.BELL_F)
    title = CharField(max_length=254)
    message = TextField()
    # To determine if the notification is specifically for single user
    for_user = BooleanField(default=False, db_index=True)
    timestamp = DateTimeField(auto_now_add=True, db_index=True)
    updated = DateTimeField(auto_now=True, db_index=True)
    viewed_by = ManyToManyField(User, blank=True, related_name='viewed_notification', db_index=True)

    objects = NotificationManager()

    def __str__(self) -> str:
        return f"{self.title}"

    def clean(self):
        super().clean()
        if (not self.for_user and self.user) or (self.for_user and not self.user):
            raise ValidationError("'User' field should not be set when 'for user' is False or vice versa.")

    def set_level(self, level_name: str) -> None:
        """
        Set notification level according to old level name, e.g. 'CRITICAL'.
        Raises ValueError on invalid level names.
        """
        self.level = self.Level.from_old_name(level_name)
        self.save()

    def mark_viewed_by(self, user) -> None:
        """Mark all viewed by user"""
        for notification in Notification.objects.all():
            notification.viewed_by.add(user)

    def mark_viewed(self, user) -> None:
        """Mark notification as viewed by a specific user."""
        self.viewed_by.add(user)
        self.save()

    def is_viewed_by_user(self, user):
        """
        Check if the notification has been viewed by the given user.
        Returns:
            True if the user has viewed the notification, False otherwise.
        """
        return self.viewed_by.filter(pk=user.pk).exists()

    def get_not_viewed_by(self, user):
        return Notification.objects.all()

    def is_viewed_by(self, user) -> bool:
        """Check if notification is viewed by a specific user."""
        return user in self.viewed_by.all()

    def is_viewed_by_all(self) -> bool:
        """Check if notification is viewed by all users."""
        if self.for_user:
            return self.user.count() == self.viewed_by.count()
        return self.users.count() == self.viewed_by.count()

    def is_viewed_by_none(self) -> bool:
        """Check if notification is viewed by no users."""
        return self.viewed_by.count() == 0
