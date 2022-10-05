from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from shop.models import ItemTrending, Item

User = get_user_model()


@receiver(post_save, sender=Item, dispatch_uid="trending_create_action")
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.trending:
            ItemTrending.objects.create(trending_item=instance)


@receiver(post_save, sender=User, dispatch_uid="employee_create_action_save")
def save_user_profile(sender, instance, **kwargs):
    instance.employee_profile.save()
