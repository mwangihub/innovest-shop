import json

from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.methods import send_channel_message
from notification.api.serializers import NotificationSerializer
from notification.models import Notification
from shop.tasks import send_mass_email_task


channel_layer = get_channel_layer()
User = get_user_model()


@receiver(post_save, sender=Notification, dispatch_uid="create_new_notification_for_user")
def create_new_notification(sender, instance, created, **kwargs):
    # message = NotifyApiWrapper().info(user=None, title='New item. Check out', message=f'{instance.title}', )
    user_email = instance.user.email if instance.user else None
    serializer = NotificationSerializer(instance)
    data = serializer.data
    if created:
        send_channel_message(
            {'data': data, 'type': Notification.__name__, },
            channel_name='shop',
            function_name='send_new_item'
        )
        if instance.user and instance.for_user:
            msg = {
                'subject': f'{instance.title}',
                'recipients': [user_email, ],
                "template": "email/notification.html",
                "json": json.dumps(data),
                'context': {"message": {"body": instance.message, "title": instance.title}, },
            }
            send_mass_email_task.delay([msg, ])
