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
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import fields


class IntegerRangeField(models.IntegerField):
    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.IntegerField.__init__(self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value': self.max_value}
        defaults.update(kwargs)
        return super(IntegerRangeField, self).formfield(**defaults)


CATEGORY_CHOICES = (("S", "Shirt"), ("SW", "Sport wear"), ("OW", "Outwear"))

LABEL_CHOICES = (("L", "Latest"), ("O", "Old-school"), ("T", "Trending"), ("B", "Best selling"), ("M", "Most sold"), ("R", "Most reviewed"), ("N", "Neutral"))

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


def items_image_path(instance, filename):
    return f'Items/{filename}'


class ItemTrending(models.Model):
    trending_item = models.ForeignKey('shop.Item', on_delete=models.CASCADE, )

    def __str__(self):
        return self.trending_item.title

    @property
    def get_main_category(self):
        category = self.trending_item.main_category_name
        return category

    @property
    def get_item_images(self):
        item_pics = self.trending_item.item_images.all()
        images = []
        for img in item_pics:
            images.append(img.image.url)
        return images


class ItemSizeByMode(models.Model):
    NONE = 'N'
    E_SMALL = 'XS'
    SMALL = 'S'
    MEDIUM = 'M'
    LARGE = 'L'
    X_LARGE = 'XL'
    XX_LARGE = 'XXL'
    SIZE_CHOICES = [(E_SMALL, 'Extra small'), (SMALL, 'Small'), (MEDIUM, 'Medium'), (LARGE, 'Large'), (X_LARGE, 'Extra large'), (XX_LARGE, 'Extra Extra large'), (NONE, 'None')]
    size = models.CharField(max_length=3, choices=SIZE_CHOICES, default=NONE, blank=True, null=True)
    item = fields.GenericRelation("shop.Item", related_query_name='item_size_mode')

    def __str__(self):
        return f'{self.id}'


class ItemSizeByNumber(models.Model):
    NONE = 'N'
    TWO = '2'
    TWO_FIVE = '2.5'
    THREE = '3'
    THREE_FIVE = '3.5'
    FOUR = '4'
    FOUR_FIVE = '4.5'
    FIVE = '5'
    FIVE_FIVE = '5.5'
    SIX = '6'
    SIX_FIVE = '6.5'
    SEVEN = '7'
    SEVEN_FIVE = '7.5'
    EIGHT = '8'
    EIGHT_FIVE = '8.5'
    NINE = '9'
    NINE_FIVE = '9.5'
    TEN = '10'
    TEN_FIVE = '10.5'
    ELEVEN = '11'
    SIZE_CHOICES = [(TWO, 'Two'), (TWO_FIVE, 'Two five'), (THREE, 'Three'), (THREE_FIVE, 'Three five'), (FOUR, 'Four'), (FOUR_FIVE, 'Four five'), (FIVE, 'Five'), (FIVE_FIVE, 'Five five'),
                    (SIX, 'Six'), (SIX_FIVE, 'Six five'), (SEVEN, 'Seven'), (SEVEN_FIVE, 'Seven five'), (EIGHT, 'Eight'), (EIGHT_FIVE, 'Eight five'),
                    (NINE, 'Nine'), (NINE_FIVE, 'Nine five'), (TEN, 'Ten'), (TEN_FIVE, 'Ten five'), (ELEVEN, 'Eleven')]
    size = models.CharField(max_length=4, choices=SIZE_CHOICES, default=NONE, blank=True, null=True)
    item = fields.GenericRelation("shop.Item", related_query_name='item_size_number')

    def __str__(self):
        return f'{self.id}'


class ItemPicture(models.Model):
    item = models.ForeignKey("shop.Item", on_delete=models.CASCADE, related_name='item_images', blank=True, null=True)
    image = models.ImageField(upload_to=items_image_path)
    current = models.BooleanField(default=False)

    def __str__(self):
        return self.image.url


class ItemColor(models.Model):
    color = models.CharField(max_length=50)

    def __str__(self):
        return self.color


class ItemSubCategory(models.Model):
    main_category = models.ForeignKey('ItemCategory', on_delete=models.CASCADE, related_name='main_cat')
    sub_category = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = 'Item sub categories'

    def __str__(self):
        return self.sub_category

    @property
    def get_main_category(self):
        return self.main_category.category


class ItemCategory(models.Model):
    category = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = 'Item categories'

    def __str__(self):
        return self.category


class ItemBrand(models.Model):
    brand = models.CharField(max_length=50)

    def __str__(self):
        return self.brand


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


class Item(models.Model):
    """
    Model that stores information about an Item
    """
    # NONE = 'N'
    # E_SMALL = 'XS'
    # SMALL = 'S'
    # MEDIUM = 'M'
    # LARGE = 'L'
    # X_LARGE = 'XL'
    # XX_LARGE = 'XXL'
    # SIZE_CHOICES = [(E_SMALL, 'Extra small'), (SMALL, 'Small'), (MEDIUM, 'Medium'), (LARGE, 'Large'), (X_LARGE, 'Extra large'), (XX_LARGE, 'Extra Extra large'), (NONE, 'None')]
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discounted_price = models.FloatField(blank=True, null=True, default=0.0)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1, default='N')
    slug = models.SlugField()
    description = models.TextField()
    brand = models.ForeignKey("ItemBrand", on_delete=models.CASCADE, blank=True, null=True, related_name="item_brand")
    color = models.ForeignKey("ItemColor", on_delete=models.SET_NULL, blank=True, null=True, related_name="item_colors")
    category = models.ForeignKey("shop.ItemSubCategory", on_delete=models.SET_NULL, blank=True, null=True, related_name="item_category")
    # size = models.CharField(max_length=3, choices=SIZE_CHOICES, default=NONE, blank=True, null=True)
    manufacturer = models.TextField(blank=True, null=True)
    stock = models.PositiveIntegerField(default=5)
    rating_count = models.PositiveIntegerField(default=0)
    rates = models.FloatField(default=0.0, validators=[MaxValueValidator(5.0), MinValueValidator(0.0)])
    trending = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(default=1)
    content_object = fields.GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.title} ID:{self.id}"

    @property
    def category_name(self):
        return self.category.sub_category

    @property
    def main_category_name(self):
        return self.category.get_main_category

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.title} ID:{self.id}")
        super(Item, self).save(*args, **kwargs)

    def get_absolute_url(self):
        slug = self.slug
        return reverse("shop")

    def get_delete_from_cart_url(self):
        return reverse("delete-from-cart", kwargs={"slug": self.slug})

    def get_add_to_cart_url(self):
        return reverse("add-to-cart", kwargs={"slug": self.slug})

    def get_reduce_qty_url(self):
        return reverse("reduce-from-cart", kwargs={"slug": self.slug})

    def get_add_qty_url(self):
        return reverse("add-items-to-cart", kwargs={"slug": self.slug})


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
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(auto_now=True)
    pay_date = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey("Address", related_name="shipping_address", on_delete=models.SET_NULL, blank=True, null=True, )
    billing_address = models.ForeignKey("Address", related_name="billing_address", on_delete=models.SET_NULL, blank=True, null=True, )
    payment = models.ForeignKey("Payment", on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey("Coupon", on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    # objects = OrderManager()

    class Meta:
        ordering = ["-ordered_date"]

    def __str__(self):
        return self.user.email

    @property
    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total

    @property
    def get_total_discount(self):
        discount = 0
        for order_item in self.items.all():
            if order_item.item.discounted_price:
                discount += order_item.get_amount_saved()
        return round(discount, 2)


class AddressQuerySet(models.QuerySet):
    def by_user(self, user):
        return self.filter(user=user)


class AddressManager(models.Manager):
    def get_queryset(self):
        return AddressQuerySet(self.model, using=self._db)

    def by_user(self, user):
        return self.get_queryset().by_user(user)


class Address(models.Model):
    """
    The address of the user.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    first_name = models.CharField(max_length=100, verbose_name="First name", blank=True, null=True, )
    last_name = models.CharField(max_length=100, verbose_name="Second name", blank=True, null=True, )
    address = models.CharField(max_length=100, blank=True, null=True, )
    state = models.CharField(max_length=100, blank=True, null=True, )
    country = CountryField(multiple=False, blank=True, null=True, default="KE")
    phone = PhoneNumberField(null=True, blank=True)
    _default = models.BooleanField(default=False)

    objects = AddressManager()

    def __str__(self):
        return f"{self.user.email}"

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
