# from django.contrib.auth.models import User
# from django.db.models.signals import pre_delete
# from django.dispatch import receiver
#
# from shop.models import *
#
#
# @receiver(pre_delete, sender=Order)
# def delete_order(sender, instance, using, **kwargs):
#     """
#     The delete_order function is used to delete all the cart items that have not been ordered.
#     This is done by checking if there are any cart items in the CartItem table that have an ordered value of False.
#     If there are, then they will be deleted from the CartItem table.
#     :param sender: Identify the model class
#     :param instance: Pass the current instance of the model that is being deleted
#     :param using: Specify the database to use for this query
#     :param **kwargs: Accept any additional keyword arguments that may have been defined by signals
#     :return: The cartitem object that is deleted
#     """
#     queryset = CartItem.objects.filter(ordered=False)
#     if queryset.count():
#         for qs in queryset:
#             if qs in queryset:
#                 qs.delete()
#
# # NOTE: Methods of saving a user with a profile
# # @receiver(post_save, sender=User)
# # def create_user_profile(sender, instance, created, **kwargs):
# #     if created:
# #         Profile.objects.create(user=instance)
#
# # @receiver(post_save, sender=User)
# # def save_user_profile(sender, instance, **kwargs):
# #     instance.profile.save()
