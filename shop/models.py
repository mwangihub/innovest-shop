"""
Shop Application is a fork of django-react-ecommerce.\n
Credits: https://github.com/justdjango/django-react-ecommerce\n
Author: https://justdjango.com/author/matt\n
"""

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.shortcuts import reverse
from django.utils.text import slugify
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField


class IntegerRangeField(models.IntegerField):
    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.IntegerField.__init__(self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value': self.max_value}
        defaults.update(kwargs)
        return super(IntegerRangeField, self).formfield(**defaults)


CATEGORY_CHOICES = (("S", "Shirt"), ("SW", "Sport wear"), ("OW", "Outwear"))

LABEL_CHOICES = (("P", "primary"), ("S", "secondary"), ("D", "danger"))

ADDRESS_CHOICES = (("B", "Billing"), ("S", "Shipping"))


class ItemReview(models.Model):
    item = models.ForeignKey("shop.Item", related_name="reviews", on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=50, blank=False)
    ratting = IntegerRangeField(min_value=1, max_value=5)
    comment = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    """
    Model that stores information about an an Item
    """
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discounted_price = models.FloatField(blank=True, null=True, default=0.0)
    category = models.CharField(max_length=200, blank=True, null=False)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    description = models.TextField()
    image = models.CharField(max_length=600)
    manufacturer = models.TextField(blank=True)
    stock = models.PositiveIntegerField(default=5)
    rating_count = models.PositiveIntegerField(default=0)
    rates = models.FloatField(default=0.0)

    # category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    # label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    # slug = models.SlugField()
    # description = models.TextField()
    # image = models.ImageField()
    # manufacturer = models.TextField(blank=True)

    # in_cart = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.title} ID:{self.id}"

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.title} ID:{self.id}")
        super(Item, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:product", kwargs={"slug": self.slug})

    def get_remove_from_cart_url(self):
        return reverse("remove-from-cart", kwargs={"slug": self.slug})

    def get_add_to_cart_url(self):
        return reverse("add-to-cart", kwargs={"slug": self.slug})


class CartItem(models.Model):
    """
    Model that stores information about an Item placed in the cart.\n
    It differs from Item model. It provides information about A SINGLE ITEM in the cart.\n
    - user => who purchased the Item?
    - ordered => was it ordered? if not don't charge it
    - quantity => how many of these Items?
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='in_cart')
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.slug}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discounted_price

    def get_amount_saved(self):
        if self.item.discounted_price:
            return self.get_total_item_price() - self.get_total_discount_item_price()
        return None

    def get_final_price(self):
        if self.item.discounted_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class OrderQuerySet(models.QuerySet):
    def not_ordered(self):
        return self.filter(ordered=False)

    def completed_by_user(self, user):
        return self.filter(ordered=True, user=user)


class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderQuerySet(self.model, using=self._db)

    def not_ordered(self):
        return self.get_queryset().not_ordered()

    def completed_by_user(self, user):
        return self.get_queryset().completed_by_user(user)


class Order(models.Model):
    """
    This model stores all Items placed in Cart, that is the order of items.\n
    - item attribute - is the CartItem (Item in the cart)
    - other attributes (user ref_code start_date ordered_date ordered shipping_address billing_address)\n
    \t are related to this order model.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=False, null=False)
    items = models.ManyToManyField(CartItem, related_name="cart_items")
    start_date = models.DateTimeField(auto_now=True)
    ordered_date = models.DateTimeField(auto_now=True)
    pay_date = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        "Address",
        related_name="shipping_address",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    billing_address = models.ForeignKey(
        "Address",
        related_name="billing_address",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    payment = models.ForeignKey(
        "Payment", on_delete=models.SET_NULL, blank=True, null=True
    )
    coupon = models.ForeignKey(
        "Coupon", on_delete=models.SET_NULL, blank=True, null=True
    )
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    objects = OrderManager()

    class Meta:
        ordering = ["-ordered_date"]

    def __str__(self):
        return self.user.email

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total

    def get_total_discount(self):
        discount = 0
        for order_item in self.items.all():
            if order_item.item.discounted_price:
                discount += order_item.get_amount_saved()
        return round(discount, 2)


class Address(models.Model):
    """
    The address of the user.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    first_name = models.CharField(max_length=100, verbose_name="First name", blank=True, null=True, )
    last_name = models.CharField(max_length=100, verbose_name="Second name", blank=True, null=True, )
    address = models.CharField(max_length=100, blank=True, null=True, )
    state = models.CharField(max_length=100, blank=True, null=True, )
    country = CountryField(multiple=False, blank=True, null=True)
    phone = PhoneNumberField(null=True, blank=True)
    saveinfo = models.BooleanField(default=False)

    def __str__(self):
        """
        The __str__ function is called when an instance of the class is printed.
        It returns a string representation of the object, which can be used for debugging and logging.
        :param self: Refer to the object itself
        :return: The string representation of the object
        :doc-author: Trelent
        """
        return "self.user.email"

    class Meta:
        verbose_name_plural = "Shipping addresses"


class Payment(models.Model):
    """
    Payment Method used by the user and the amount.
    PayPal, Mpesa e.t.c
    """
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email


class Coupon(models.Model):
    """
    Coupon awarded to the user. If the code of this coupon exists in any previous orders,\n
    Its considered expired.
    """
    code = models.CharField(max_length=15)
    amount = models.FloatField()
    redeemed = models.BooleanField(default=False)

    def __str__(self):
        return self.code

    def get_coupon_amount(self):
        return self.amount


class Refund(models.Model):
    """
    Refund for any order with a reason, only if it is accepted
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


class CustomerPurchaseProfile(models.Model):
    """
    This model stores user, stripe customer id & one click purchasing functionality.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email


class ItemSample(models.Model):
    image = models.ImageField()
    name = models.CharField(max_length=50, blank=False)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-pk"]

    def __str__(self):
        return self.name


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = CustomerPurchaseProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)
