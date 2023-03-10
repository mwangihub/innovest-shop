from asgiref.sync import async_to_sync as sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.forms import model_to_dict

from shop.api.serializers import ItemSerializer
from shop.models import (ItemTrending, Item, GenericForeignKeyModel, UserInstallmentPayDetail)
from shop.notify import NotifyApiWrapper

channel_layer = get_channel_layer()
User = get_user_model()


@receiver(post_save, sender=UserInstallmentPayDetail, dispatch_uid="create_user_installment_pay_detail")
def create_user_installment_pay_detail(sender, instance, created, **kwargs):
    pass


def send_channel_message(data, channel_name=None, function_name=None):
    sync(channel_layer.group_send)(
        f'{channel_name}', {
            'type':
                f'{function_name}', 'text': data
        })


@receiver(pre_save, sender=Item, dispatch_uid="pre_create_new_item")
def pre_create_new_item(sender, instance, *args, **kwargs):
    pass
    # related_objects = GenericForeignKeyModel.objects.filter(db_type__in=instance.db_type)
    # print(instance.related_db.all())
    # instance.related_db.set(related_objects)


@receiver(post_save, sender=Item, dispatch_uid="create_new_item")
def create_new_item(sender, instance, created, **kwargs):
    pass
    # Use the `__in` lookup to filter the queryset in a single query
    # related_objects = GenericForeignKeyModel.objects.filter(db_type__in=instance.db_type)
    # Use the `set` method to set the ManyToManyField to the related objects
    # print(instance.related_db.all())
    # instance.related_db.set(related_objects)
    # item = ItemSerializer(instance=instance, many=False).data
    # message = NotifyApiWrapper().info(user=None, title='New item. Check out', message=f'{instance.title}', )
    # send_channel_message({
    #     'data': item,
    #     'notification': message,
    #     'type': Item.__name__,
    #     'created': True,
    #     'purchased': False
    # }, channel_name='shop', function_name='send_new_item')
