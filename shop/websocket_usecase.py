from shop.models import Notification
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()


@database_sync_to_async
def set_notification_view(msg, user, session_id):
    """
    Set Notification view to True for user
    TODO: If not user: Implement with session_id or just invalidate QS based on session.
    """
    try:
        notification = Notification.objects.get(id=msg["id"], user=user)
        notification.mark_viewed()
    except Notification.DoesNotExist:
        notification = Notification.objects.get(id=msg["id"])


@database_sync_to_async
def set_all_notification_view(msg, user, session_id):
    """
    Set Notification view to True for user
    """
    queryset = Notification.objects.filter(user=user)
    if queryset.exists():
        for notification in queryset:
            notification.mark_viewed()
        async_to_sync(channel_layer.group_send)('shop_messages', {'type': 'send_shop_message', 'text': {
            "dispatch": "getNotifications",
            "type": "dispatch_getNotifications"
        }})


async def switch_message(message, scope):
    session_id = scope["headers"]
    if message.get("setNotification_view", None):
        await set_notification_view(message, scope['user'], session_id)
    if message.get("setAllNotification_view", None):
        await set_all_notification_view(message, scope['user'], session_id)
