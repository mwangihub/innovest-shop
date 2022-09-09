
from django.conf import settings

from email.mime import image
from pyexpat import model
from tokenize import maybe

from rest_framework import serializers
from shop.models import *

from django_countries.serializer_fields import CountryField
from django_countries.serializers import CountryFieldMixin
from django.contrib.auth import get_user_model

User = get_user_model()


def _user(request=None):
    if not settings.DEV_MODE:
        return request.user
    return User.objects.get(email="pmwassini@gmail.com")


# class ItemSampleSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = ItemSample
#         fields = "__all__"


class AddressSerializer(CountryFieldMixin, serializers.ModelSerializer):
    country = CountryField()
    country_full = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = (
            "id",
            "user",
            "address",
            "state",
            "country",
            "country_full",
            "phone",
            "saveinfo",
            "first_name",
            "last_name",
        )

    def get_country_full(self, address):
        return address.country.name

    def validate(self, attrs):
        user = _user(self.context['request'])
        country = attrs.get('country', None)
        if not country:
            attrs['country'] = "KE"
        attrs['user'] = user
        return attrs


class ItemReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemReview
        fields = "__all__"


class ItemSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    cart_count = serializers.SerializerMethodField()
    # image = serializers.SerializerMethodField()
    # remove_from_cart = serializers.SerializerMethodField()
    # add_to_cart = serializers.SerializerMethodField()
    reviews = ItemReviewSerializer(many=True, read_only=False)

    class Meta:
        model = Item
        fields = (
            "id",
            "title",
            "price",
            "discounted_price",
            "category",
            "label",
            "slug",
            "description",
            "image",
            "stock",
            "rating_count",
            "rates",
            "reviews",
            "cart_count",
        )

    def get_label(self, obj):
        return obj.get_label_display()

    def get_image(self, obj):
        product_image = obj.image
        return self.context["request"].build_absolute_uri(product_image)

    # def get_reviews(self, obj):
    #     # note the related_name in the model
    #     return  ItemReviewSerializer(obj.reviews.all(), many=True).data

    def get_category(self, obj):
        # return obj.get_category_display()
        return obj.category


    def get_cart_count(self, obj):
        item_in_cart = obj.in_cart.all().filter(item=obj, ordered=False)
        if item_in_cart.exists():
            return item_in_cart[0].quantity

    def get_remove_from_cart(self, obj):
        obj_url = obj.get_remove_from_cart_url()
        return self.context["request"].build_absolute_uri(obj_url)

    def get_add_to_cart(self, obj):
        obj_url = obj.get_add_to_cart_url()
        return self.context["request"].build_absolute_uri(obj_url)


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = (
            "id",
            "user",
            "item",
            "quantity",
            "total",
            "amnt_saved",
        )

    total = serializers.SerializerMethodField()
    amnt_saved = serializers.SerializerMethodField()
    item = serializers.SerializerMethodField()

    def get_item(self, obj):
        return ItemSerializer(obj.item, read_only=False).data

    def get_total(self, obj):
        return obj.get_final_price()

    def get_amnt_saved(self, obj):
        return obj.get_amount_saved()


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


# "start_date","ordered_date","ordered","shipping_address","billing_address",
# "payment","coupon","being_delivered","received","refund_requested","refund_granted","ref_code",
class OrderSerializer(serializers.ModelSerializer):
    cart_items = serializers.SerializerMethodField()
    order_total = serializers.SerializerMethodField()
    total_discount = serializers.SerializerMethodField()
    coupon = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    payment = serializers.SerializerMethodField()
    ref_code = serializers.SerializerMethodField()
    ordered = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            "id",
            "cart_items",
            "order_total",
            "total_discount",
            "coupon",
            "address",
            "payment",
            "ref_code",
            "ordered",
            "start_date",
            "ordered"

        )

    def get_ordered(self, obj):
        return obj.ordered

    def get_ref_code(self, obj):
        return obj.ref_code

    def get_cart_items(self, obj):
        return CartItemSerializer(obj.items.all(), many=True).data

    def get_order_total(self, obj):
        return obj.get_total()

    def get_total_discount(self, obj):
        return obj.get_total_discount()

    def get_coupon(self, obj):
        return CouponSerializer(obj.coupon, many=False).data

    def get_address(self, obj):
        return AddressSerializer(obj.billing_address, many=False).data

    def get_payment(self, obj):
        return PaymentSerializer(obj.payment, many=False).data
