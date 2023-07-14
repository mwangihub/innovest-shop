import json

from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms.models import model_to_dict

from core.methods import send_channel_message
from notification.models import Notification
from shop.models import (UserInstallmentPayDetail, Order, Item, Payment)
from .api.serializers import ItemSerializer, PaymentSerializer
from .tasks import send_mass_email_task

channel_layer = get_channel_layer()
User = get_user_model()


@receiver(post_save, sender=UserInstallmentPayDetail, dispatch_uid="create_user_installment_pay_detail")
def create_user_installment_pay_detail(sender, instance, created, **kwargs):
    """
    A lot of logic should be added here.
    - When order is complete we create order object
    """


@receiver(post_save, sender=Payment, dispatch_uid="create_payment")
def create_payment(sender, instance, created, **kwargs):
    """ """
    if created:
        serializer = PaymentSerializer(instance)
        data = serializer.data
        message = f"We are in receipt of your payment of Ksh.{instance.amount} \
            through {instance.mpesa_no}. Use Charge id: {instance.stripe_charge_id}\
             to track paid items."
        title = "Payment was successful."
        notification = Notification.objects.notify(
            title,
            message,
            user=instance.user,
            for_user=True
        )
        recipients = ["pmwassini@gmail.com"]

        try:
            user_email = instance.user.email
            recipients.append(user_email)
        except Exception as e:
            pass
        msg = {
            'subject': title,
            'recipients': recipients,
            'template': "email/payment.html",
            "json": json.dumps(data),
            'context': {"message": message, },
        }
        send_mass_email_task.delay([msg, ])


@receiver(post_save, sender=Item, dispatch_uid="create_new_item")
def create_new_item(sender, instance, created, **kwargs):
    """A lot of logic should be added here."""
    send_channel_message(
        {'data': {"created": False, "action": None}, 'type': Item.__name__, },
        channel_name='shop',
        function_name='send_new_item'
    )
    if created:
        item = ItemSerializer(instance)
        send_channel_message(
            {'data': {"created": True, "item": item.data}, 'type': Item.__name__, },
            channel_name='shop',
            function_name='send_new_item'
        )


def send_mail_signal(instance, title=None, template=None, message=None):
    order_items = instance.items.all()
    items = []
    if not template:
        template = "email/message.html",
    for order_item in order_items:
        item = order_item.item
        item_dict = {
            'title': item.title,
            'price': item.price,
            'discounted_price': item.discounted_price
        }
        items.append(item_dict)
    instance_dict = model_to_dict(instance, )
    instance_dict['items'] = items
    msg = {
        'subject': f'{instance.ref_code}: {title}',
        'recipients': [instance.user.email, ],
        'template': template,
        "json": json.dumps(instance_dict),
        'context': {"message": message, },
    }
    send_mass_email_task.delay([msg, ])


class PostOrderOrdered:
    @staticmethod
    @receiver(post_save, sender=Order, dispatch_uid="post_order_ordered")
    def handle_post_order_ordered(sender, instance, created, **kwargs):
        """Inform all users on items purchased"""
        ordered = instance.ordered
        if ordered and instance.being_delivered:
            PostOrderOrdered.handle_being_delivered(instance)
        elif ordered and instance.received:
            PostOrderOrdered.handle_received(instance)
        elif ordered and instance.refund_requested:
            PostOrderOrdered.handle_refund_requested(instance)
        elif ordered and instance.refund_granted:
            PostOrderOrdered.handle_refund_granted(instance)
        elif ordered and instance.get_first_ordered:
            PostOrderOrdered.handle_first_ordered(instance)

    @staticmethod
    def handle_being_delivered(instance):
        send_mail_signal(
            instance,
            title=' Order dispatched',
            message=f"Please note that your order No. {instance.ref_code} has been dispatched to your address"
        )

    @staticmethod
    def handle_received(instance):
        send_mail_signal(
            instance,
            title=' Order received',
            message=f"Good shopping with us. Thank you for confirming receipt of the same."
        )

    @staticmethod
    def handle_refund_requested(instance):
        send_mail_signal(
            instance,
            title=' Refund requested for this order',
            message=f"We have received your request to cancel order no. {instance.ref_code}. Reasons and possibilities are being evaluated."
        )

    @staticmethod
    def handle_refund_granted(instance):
        send_mail_signal(
            instance,
            title=' Refund granted',
            message=f"Please note that refund of order no. {instance.ref_code} has been granted. You will receive the refund on the same method used to pay"
        )

    @staticmethod
    def handle_first_ordered(instance):
        titles = []
        buyer = instance.user.email.split("@")[0]
        order_items = instance.items.all()
        for order_item in order_items:
            item = order_item.item
            titles.append(item.title)
        send_channel_message({
            'data': titles,
            'notification': f"{buyer} just purchased: ",
            'type': Order.__name__,
            'user': instance.user.email

        }, channel_name='shop', function_name='send_new_item')
        send_mail_signal(
            instance,
            title='Order placed ',
            message="Thank you for your order. It is being processed. We inform you soon as it is dispatched to your address"
        )
