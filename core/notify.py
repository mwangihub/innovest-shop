
class NotifyApiWrapper:
    """Wrapper to create notify API."""

    def __call__(self, *args, **kwargs):  # provide old API for backwards compatibility
        return self._add_notification(*args, **kwargs)

    def danger(self, user: object, title: str, message: str = None) -> object:
        """Add danger notification for user."""
        return self._add_notification(user=user, title=title, message=message, level="danger", icon='shield-fill-exclamation')

    def info(self, user: object, title: str, message: str = None) -> object:
        """Add info notification for user."""
        return self._add_notification(user=user, title=title, message=message, level="info", icon='bell-fill')

    def success(self, user: object, title: str, message: str = None) -> object:
        """Add success notification for user."""
        return self._add_notification(user=user, title=title, message=message, level="success", icon='check-circle-fill')

    def warning(self, user: object, title: str, message: str = None) -> object:
        """Add warning notification for user."""
        return self._add_notification(user=user, title=title, message=message, level="warning", icon='exclamation-triangle-fill')

    def _add_notification(self, user: object, title: str, message: str = None, level: str = None, icon: str = None) -> object:
        from .models import Notification
        model = self.__str__()
        obj = Notification.objects.notify_user(user=user, title=title, message=message, level=level, icon=icon)
        return obj


notify = NotifyApiWrapper()
