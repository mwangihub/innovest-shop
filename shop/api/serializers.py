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


class ItemSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemSubCategory
        fields = '__all__'


class ItemCategorySerializer(serializers.ModelSerializer):
    sub_categories = serializers.SerializerMethodField()

    class Meta:
        model = ItemCategory
        fields = '__all__'

    def get_sub_categories(self, obj):
        req = self.context
        qs = obj.main_cat.all()
        return ItemSubCategorySerializer(qs, many=True).data


class ItemTrendingSerializer(serializers.ModelSerializer):
    get_main_category = serializers.ReadOnlyField()
    get_item_images = serializers.ReadOnlyField()

    class Meta:
        model = ItemTrending
        fields = '__all__'


class ItemReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemReview
        fields = "__all__"


class ItemImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPicture
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()
    # size = serializers.SerializerMethodField()
    category_name = serializers.ReadOnlyField()
    main_category_name = serializers.ReadOnlyField()
    reviews = ItemReviewSerializer(many=True, read_only=False)
    item_images = ItemImagesSerializer(many=True, read_only=False)
    # delete_from_cart_url = serializers.SerializerMethodField()
    delete_from_cart_url = serializers.URLField(source='get_delete_from_cart_url', read_only=True)
    add_to_cart_url = serializers.URLField(source='get_add_to_cart_url', read_only=True)
    reduce_qty_url = serializers.URLField(source='get_reduce_qty_url', read_only=True)
    add_qty_url = serializers.URLField(source='get_add_qty_url', read_only=True)
    cart_count = serializers.SerializerMethodField()
    size_choices = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = '__all__'

    def get_label(self, obj):
        req = self.context
        return obj.get_label_display()

    def get_size_choices(self, obj):
        if hasattr(obj.content_type, 'model_class'):
            if hasattr(obj.content_type.model_class(), 'SIZE_CHOICES'):
                return obj.content_type.model_class().SIZE_CHOICES
        req = self.context
        return None

    def get_cart_count(self, obj):
        item_in_cart = obj.in_cart.all().filter(item=obj, ordered=False)
        if item_in_cart.exists():
            return item_in_cart[0].quantity

    def get_add_to_cart_url(self, obj):
        obj_url = obj.get_add_to_cart_url()
        return self.context["request"].build_absolute_uri(obj_url)


class AddressSerializer(CountryFieldMixin, serializers.ModelSerializer):
    country = CountryField()
    country_full = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = ("id", "user", "address", "state", "country", "country_full", "phone", "first_name", "last_name", "_default")

    def get_country_full(self, address):
        req = self.context
        return address.country.name

    def validate(self, attrs):
        user = _user(self.context['request'])
        country = attrs.get('country', None)
        if not country:
            attrs['country'] = "KE"
        attrs['user'] = user
        return attrs


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
        return ItemSerializer(obj.item, read_only=False, context=self.context).data

    def get_total(self, obj):
        req = self.context
        return obj.get_final_price()

    def get_amnt_saved(self, obj):
        req = self.context
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
    # cart_items = serializers.SerializerMethodField()
    items = CartItemSerializer(read_only=False, many=True)
    order_total = serializers.SerializerMethodField()
    total_discount = serializers.SerializerMethodField()
    coupon = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    payment = serializers.SerializerMethodField()
    ref_code = serializers.SerializerMethodField()
    ordered = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = '__all__'

    def get_ordered(self, obj):
        return obj.ordered

    def get_ref_code(self, obj):
        return obj.ref_code

    def get_cart_items(self, obj):
        return CartItemSerializer(obj.cart_items.all(), many=True).data

    def get_order_total(self, obj):
        return obj.get_total

    def get_total_discount(self, obj):
        return obj.get_total_discount

    def get_coupon(self, obj):
        return CouponSerializer(obj.coupon, many=False).data

    def get_address(self, obj):
        return AddressSerializer(obj.billing_address, many=False).data

    def get_payment(self, obj):
        return PaymentSerializer(obj.payment, many=False).data
