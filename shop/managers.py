import logging

from django.db import models

logger = logging.getLogger(__name__)


class DefaultQuerySet(models.QuerySet):
    """Custom QuerySet"""


class ShippingChargeManager(models.Manager):

    def get_queryset(self):
        return DefaultQuerySet(self.model, using=self._db)

    def get_no_item(self):
        return self.filter(item=None).prefetch_related("item")

    def get_for_item(self, item):
        return self.filter(item=item).prefetch_related("item")


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

    def get_first_ordered(self):
        """We are assuming that the order is first placed"""
        return self.filter(
            ordered=True,
            being_delivered=False,
            received=False,
            refund_requested=False,
            refund_granted=False,
        )


class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)

    def not_ordered(self):
        return self.get_queryset().not_ordered()

    def completed_by_user(self, user):
        return self.get_queryset().completed_by_user(user)

    def get_first_ordered(self, user):
        return self.get_queryset().get_first_ordered()


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
