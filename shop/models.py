"""
Shop Application is a fork of django-react-ecommerce.\n
Credits: https://github.com/justdjango/django-react-ecommerce\n
Author: https://justdjango.com/author/matt\n
"""
import logging
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes import fields
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count
from django.shortcuts import reverse
from django.utils.text import slugify
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

from .managers import (AddressManager, ShippingChargeManager, OrderManager)

User = get_user_model()
logger = logging.getLogger(__name__)

RELATED_DB_TYPES = (("NE", 'None'), ("SN", 'Size by number'), ("SM", 'Size by mode'), ("CD", 'Coloured'), ("OR", 'Original'), ("RF", 'Refurbished'), ("BR", 'Branded'),)

CATEGORY_CHOICES = (("S", "Shirt"), ("SW", "Sport wear"), ("OW", "Outwear"))

LABEL_CHOICES = (("L", "Latest"), ("O", "Old-school"), ("T", "Trending"), ("B", "Best selling"), ("M", "Most sold"), ("R", "Most reviewed"), ("N", "Neutral"))

ADDRESS_CHOICES = (("B", "Billing"), ("S", "Shipping"))

ITEM_RATINGS = ((5, "5 stars"), (4, "4 stars"), (3, "3 stars"), (2, "2 stars"), (1, "1 star"),)


def items_image_path(instance, filename):
    return f'Items/{filename}'


class IntegerRangeField(models.IntegerField):
    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.IntegerField.__init__(self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value': self.max_value}
        defaults.update(kwargs)
        return super(IntegerRangeField, self).formfield(**defaults)


class RELATED_DB_TYPES_FOR_ITEMS(models.Model):
    db_type = models.CharField(choices=RELATED_DB_TYPES, default='NE', max_length=2)

    class Meta:
        verbose_name = 'related DB type'
        verbose_name_plural = 'related DB types'

    def __str__(self):
        return self.get_db_type_display()


class Town(models.Model):
    name = models.CharField(max_length=55)

    def __str__(self):
        return self.name


class GenericForeignKeyModel(models.Model):
    db_type = models.CharField(choices=RELATED_DB_TYPES, default='NE', max_length=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.content_type}'


class ItemManufacturer(models.Model):
    item = models.ForeignKey("shop.Item", on_delete=models.CASCADE, default=1)
    manufacturer_name = models.CharField(max_length=255, blank=False)
    vendor_name = models.CharField(max_length=255, help_text="Use 255 words to introduce vendors name", blank=True, null=True)
    location_details = models.CharField(max_length=255, blank=False)
    factory_information = models.CharField(max_length=555, help_text="Use 500 to describe factory")
    product_instruction = models.TextField(help_text="Give instructions where needed")
    social_links = models.CharField(max_length=300, help_text="Use commas to separate links, e.g 'website:www.factory.com/factory_name', ... ")

    def __str__(self):
        return f'{self.manufacturer_name}-{self.item.title}'


class ItemReview(models.Model):
    ITEM_RATINGS = ITEM_RATINGS
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user_reviews", on_delete=models.SET_NULL, default=1, blank=True, null=True)
    item = models.ForeignKey("shop.Item", related_name="reviews", on_delete=models.CASCADE, default=1)
    email = models.EmailField(blank=True, null=True)
    name = models.CharField(max_length=50, blank=False)
    ratings = models.PositiveSmallIntegerField(choices=ITEM_RATINGS, default=5)
    comment = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ItemTrending(models.Model):
    trending_item = models.ForeignKey('shop.Item', on_delete=models.CASCADE, )

    def __str__(self):
        return self.trending_item.title

    @property
    def get_item(self):
        item = {
            "title": self.trending_item.title,
            "price": self.trending_item.price,
            "category": self.trending_item.main_category_name,
        }
        return item

    def get_item_images(self, request):
        item_pics = self.trending_item.item_images.all()
        images = []
        for img in item_pics:
            absolute_url = request.build_absolute_uri(img.image.url)
            images.append(absolute_url)
            # images.append(img.image.url)
        return images


class ItemSizeByMode(models.Model):
    NONE = 'N'
    E_SMALL = 'XS'
    SMALL = 'S'
    MEDIUM = 'M'
    LARGE = 'L'
    X_LARGE = 'XL'
    XX_LARGE = 'XXL'
    SIZE_CHOICES = [(E_SMALL, 'Extra small'), (SMALL, 'Small'), (MEDIUM, 'Medium'), (LARGE, 'Large'),
                    (X_LARGE, 'Extra large'), (XX_LARGE, 'Extra Extra large'), (NONE, 'None')]
    size = models.CharField(max_length=3, choices=SIZE_CHOICES, default=NONE, blank=True, null=True)
    item = fields.GenericRelation("shop.Item", related_query_name='item_size_mode')

    def __str__(self):
        return f'{self.size}'


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
    SIZE_CHOICES = [(NONE, 'None'), (TWO, 'Two'), (TWO_FIVE, 'Two five'), (THREE, 'Three'), (THREE_FIVE, 'Three five'),
                    (FOUR, 'Four'), (FOUR_FIVE, 'Four five'), (FIVE, 'Five'), (FIVE_FIVE, 'Five five'),
                    (SIX, 'Six'), (SIX_FIVE, 'Six five'), (SEVEN, 'Seven'), (SEVEN_FIVE, 'Seven five'),
                    (EIGHT, 'Eight'), (EIGHT_FIVE, 'Eight five'),
                    (NINE, 'Nine'), (NINE_FIVE, 'Nine five'), (TEN, 'Ten'), (TEN_FIVE, 'Ten five'), (ELEVEN, 'Eleven')]
    size = models.CharField(max_length=4, choices=SIZE_CHOICES, default=NONE, blank=True, null=True)
    item = fields.GenericRelation("shop.Item", related_query_name='item_size_number')

    def __str__(self):
        return f'{self.get_size_display()}'


class ItemPicture(models.Model):
    item = models.ForeignKey("shop.Item", on_delete=models.CASCADE, related_name='item_images', blank=True, null=True)
    image = models.ImageField(upload_to=items_image_path)
    current = models.BooleanField(default=False)

    def __str__(self):
        return self.image.url


class ItemColorChoice(models.Model):
    item = models.ForeignKey("shop.Item", on_delete=models.CASCADE)
    color = models.ForeignKey("shop.ItemColor", on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f'{self.item.title} - {self.color}'


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


class ItemBrandName(models.Model):
    brand = models.CharField(max_length=50)
    brand_logo = models.ImageField(upload_to='items/brands/logo/', blank=True, null=True)

    def __str__(self):
        return f'{self.brand}'


class ItemBrand(models.Model):
    item = models.ForeignKey("shop.Item", on_delete=models.SET_NULL, related_name="branded_item", blank=True, null=True)
    brand_name = models.ForeignKey("shop.ItemBrandName", on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f'{self.brand_name.brand}'


class Item(models.Model):
    """
    Model that stores information about an Item
    """
    title = models.CharField(max_length=255)
    price = models.FloatField()
    pay_with_installment = models.BooleanField(default=False)
    discounted_price = models.FloatField(blank=True, null=True, default=0.0)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1, default='N')
    category = models.ForeignKey("shop.ItemSubCategory", on_delete=models.SET_NULL, blank=True, null=True, related_name="item_category")
    stock = models.PositiveIntegerField(default=5)
    brand = models.ForeignKey("shop.ItemBrand", on_delete=models.SET_NULL, related_name="standard_brand", blank=True, null=True)
    color = models.ForeignKey("shop.ItemColor", on_delete=models.SET_NULL, blank=True, null=True)
    manufacturer = models.ForeignKey("shop.ItemManufacturer", on_delete=models.SET_NULL, related_name="item_manufacturer", blank=True, null=True)
    description = models.TextField(default="This is the Item description")
    db_type = models.ManyToManyField("shop.RELATED_DB_TYPES_FOR_ITEMS", related_name="related_db_types", blank=True)

    available_brands = models.ManyToManyField("shop.ItemBrand", related_name="item_available_brands", blank=True)
    available_colors = models.ManyToManyField("shop.ItemColorChoice", related_name="item_available_colors", blank=True)

    rates = models.FloatField(default=0.0)
    average_rates = models.FloatField(default=0.0)

    rating_count = models.ManyToManyField("shop.ItemReview", related_name="item_reviews", blank=True)
    related_db = models.ManyToManyField(GenericForeignKeyModel, blank=True)
    slug = models.SlugField(blank=True, null=True, max_length=255)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.title} ID:{self.id}"

    def save(self, *args, **kwargs):
        try:
            if self.rating_count:
                rates = 0
                queryset = self.rating_count.all().values("ratings")
                for qs in queryset:
                    rates += qs['ratings']
                self.rates = rates
                try:
                    self.average_rates = rates / queryset.count()
                except ZeroDivisionError:
                    pass
                except Exception as e:
                    pass
        except Exception as e:
            pass
        self.slug = slugify(f"{self.title}")
        super(Item, self).save(*args, **kwargs)

    def get_lines_list(self):
        return self.description.split('\n')

    def set_lines_list(self, lines):
        self.description = '\n'.join(lines)

    description_list = property(get_lines_list, set_lines_list)

    @property
    def category_name(self):
        return self.category.sub_category

    @property
    def main_category_name(self):
        return self.category.get_main_category

    @property
    def get_ratings(self):
        ratings = self.rating_count.all().values("ratings").annotate(count=Count("ratings"))
        return [{"rating": r["ratings"], "count": r["count"]} for r in ratings]

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


class ShippingCharge(models.Model):
    """
    Shipping charges varies with locations. Merchant might add an area he feels its under his jurisdiction
    Because of unpredictable future events, this table should be separate in order to allow merchant
    to be flexible.

    NOTE:For this case, item can be blank for the purpose of InstallmentDetail, but it must be associated with a town/location
    """
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, blank=True, null=True)
    town = models.ForeignKey("shop.Town", on_delete=models.CASCADE)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)
    for_item = models.BooleanField(default=False)
    objects=ShippingChargeManager()
    def __str__(self):
        """
        Shortened title and area code
        """
        default = f'{self.town.name}-{self.shipping_cost}'
        if not self.item:
            return default
        title = self.item.title.split()
        short_title = " ".join(title[:3])
        return f'{short_title}-{default}'

    def save(self, *args, **kwargs):
        """Shipping charge for Item must be present to allow functionality to be run"""
        if (self.item and not self.for_item) and (not self.item and self.for_item):
            raise ValidationError(f'Adding "item" must also set "for_item" to True and vice versa')
        super().save(*args, **kwargs)


class CartItem(models.Model):
    """
    Model that stores information about an Item placed in the cart.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='in_cart')
    quantity = models.IntegerField(default=1)
    chosen_size = models.CharField(max_length=25, blank=True, null=True)
    chosen_color = models.CharField(max_length=25, blank=True, null=True)
    chosen_brands = models.CharField(max_length=25, blank=True, null=True)
    describe = models.TextField(help_text="For example, match quantity with color per item or brand.", blank=True, null=True)

    class Meta:
        indexes = [models.Index(fields=['user', 'ordered']), ]

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


class Order(models.Model):
    """
    This model stores all Items placed in Cart, that is the order of items.\n
    - item attribute - is the CartItem (Item in the cart)
    - other attributes (user ref_code start_date ordered_date ordered shipping_address billing_address)\n
    \t are related to this order model.
    TODO:Shipping Charges should be based on KGS or Location Area. What about item being processed?
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=False, null=False)
    items = models.ManyToManyField(CartItem, related_name="cart_items")
    shipping_address = models.ForeignKey("Address", related_name="shipping_address", on_delete=models.SET_NULL, blank=True, null=True, )
    billing_address = models.ForeignKey("Address", related_name="billing_address", on_delete=models.SET_NULL, blank=True, null=True, )
    payment = models.ForeignKey("Payment", on_delete=models.SET_NULL, related_name="orders", blank=True, null=True)
    coupon = models.ForeignKey("Coupon", on_delete=models.SET_NULL, blank=True, null=True)
    shipping_charges = models.ForeignKey("shop.ShippingCharge", on_delete=models.SET_NULL, blank=True, null=True)
    installment_item = models.ForeignKey("shop.ItemInstallmentDetail", on_delete=models.SET_NULL, blank=True, null=True)
    # payment = models.ForeignKey("Payment", on_delete=models.SET_NULL, related_name="orders", blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(auto_now=True)
    pay_date = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=False)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    objects = OrderManager()

    class Meta:
        ordering = ["-ordered_date"]

    def __str__(self):
        return f'{self.id}'

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

    @property
    def get_first_ordered(self):
        """We are assuming that the order is first placed"""
        return (
                self.ordered and not
        self.being_delivered and not
                self.received and not
                self.refund_requested and not
                self.refund_granted
        )


class Address(models.Model):
    """
    The address of the user.
    """
    B = 'B'
    S = 'S'
    ADDRESS_CHOICES = [(B, 'Billing'), (S, 'Shipping'), ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="address", default=1)
    email = models.EmailField(max_length=100, verbose_name="Alternative email", blank=True, null=True, )
    first_name = models.CharField(max_length=100, verbose_name="First name", blank=True, null=True, )
    last_name = models.CharField(max_length=100, verbose_name="Second name", blank=True, null=True, )
    address = models.CharField(max_length=100, blank=True, null=True, )
    state = models.CharField(max_length=100, blank=True, null=True, )
    country = CountryField(multiple=False, blank=True, null=True, default="KE")
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES, default=B)
    phone = PhoneNumberField(null=True, blank=True)
    _default = models.BooleanField(default=False)

    objects = AddressManager()

    def __str__(self):
        return f"{self.user}"

    class Meta:
        verbose_name_plural = "Shipping addresses"


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
        return self.stripe_customer_id


class Payment(models.Model):
    """
    Payment Method used by the user and the amount. For this case we are using Mpesa payment gateway
    We are storing the number used to make payment and the amount
    TODO:Shipping field should be filled to avoid records having issues in an event shipping charge cost of
            a location changes
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    mpesa_no = PhoneNumberField(null=True, blank=True)
    amount = models.FloatField(verbose_name="goods_cost")
    shipping = models.CharField(max_length=100, blank=True, null=True)
    installment_item = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    stripe_charge_id = models.CharField(max_length=255, null=True, blank=True, default=uuid.uuid4)

    def __str__(self):
        return f"{self.user.email}"


class ItemInstallmentDetail(models.Model):
    """
    Stores Instalment details of the item. An Item can have different periods and deposit amounts
    This impacts the total cost of the item
    """
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=100)
    payment_period = models.PositiveIntegerField(default=2)

    class Meta:
        ordering = ['payment_period']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shipping_charges = None

    def __str__(self):
        return f"{self.item.title}"

    def save(self, *args, **kwargs):
        """Shipping charge for Item must be present to allow functionality to be run"""
        if self.item:
            charges_qs = ShippingCharge.objects.get_for_item(self.item)
            if not charges_qs.exists():
                raise ValidationError(f'First add shipping charges for {self.item.title}')
        super().save(*args, **kwargs)

    def next_amount(self):
        """Returns the amount to pay on the first creating instance"""
        return (self.total_cost - self.deposit_amount) / self.payment_period


class UserInstallmentPayDetail(models.Model):
    """
    Stores information of user and Item being paid to track all installments. For this case,
    we are using MPESA Payment gateway through phone number. required_period,selected_shipping_charges
    depends on installment_item selected by user
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    selected_address = models.ForeignKey("shop.Address", on_delete=models.SET_NULL, blank=True, null=True)
    installment_item = models.ForeignKey("shop.ItemInstallmentDetail", on_delete=models.CASCADE)
    selected_shipping_charges = models.ForeignKey("shop.ShippingCharge", on_delete=models.SET_NULL, blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)
    remaining_balance = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)
    next_amount_to_pay = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, default=0)
    payment_period_start_date = models.DateField(auto_now_add=True, blank=True, null=True, verbose_name="start date")
    payment_due_date = models.DateField(blank=True, null=True)
    paid_for_period = models.PositiveIntegerField(blank=True, null=True, default=0)
    required_period = models.PositiveIntegerField(blank=True, null=True)
    mpesa_no = PhoneNumberField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    # default=datetime.datetime.now
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-id']
    def __str__(self):
        return f'{self.user} '

    def save(self, *args, **kwargs):
        """
        We need to find a way to get accurate remaining_balance
        """
        existing_installs = UserInstallmentPayDetail.objects.filter(
            installment_item__item__title=self.installment_item.item.title,
            amount_paid__lt=1,
            payment_due_date=None
        )
        if existing_installs.exists():
            existing_installs.delete()

        super(UserInstallmentPayDetail, self).save(*args, **kwargs)

    @property
    def payment_period_duration_first(self):
        """
        The calculate_payment_period_duration method calculates the duration of
        the payment period by subtracting the payment_period_start_date from the
        payment_due_date. The result is a timedelta object that represents the
        duration of the payment period in days.
        """
        payment_period_duration = self.payment_due_date - self.payment_period_start_date
        return payment_period_duration

    @property
    def payment_period_duration(self):
        """
        The calculate_payment_period_duration method calculates the number of monthly
        installments by dividing the timedelta object by 30 days (the average number
        of days in a month
        item_total_cost = self.installment_item.total_cost
        time_period = self.installment_item.payment_period
        deposit_amount = self.installment_item.deposit_amount
        per_installment_amount = (item_total_cost-deposit_amount)/time_period
        """
        payment_period_duration = self.payment_due_date - self.payment_period_start_date
        number_of_monthly_installments = (payment_period_duration / timedelta(days=30)).days + 1
        return number_of_monthly_installments

    @property
    def get_remaining_balance(self):
        return self.remaining_balance

    @property
    def next_payment_amount(self):
        return self.installment_item.next_amount()

    @property
    def actual_total(self):
        if self.selected_shipping_charges:
            return self.installment_item.total_cost + self.selected_shipping_charges.shipping_cost
        return self.installment_item.total_cost
