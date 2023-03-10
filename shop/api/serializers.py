from django.contrib.auth import get_user_model
from django_countries.serializer_fields import CountryField
from django_countries.serializers import CountryFieldMixin
from rest_framework import serializers

from shop.models import *

User = get_user_model()


def _user(request=None):
    if not settings.DEV_MODE:
        if request.user.is_authenticated:
            return request.user
        return None
    return User.objects.get(email="petermwangi@gmail.com")


class TownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Town
        fields = "__all__"


class ShippingLocationChargesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingLocationCharges
        fields = "__all__"


class GenericForeignKeyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenericForeignKeyModel
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"


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


class ItemImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPicture
        fields = '__all__'


class ItemTrendingSerializer(serializers.ModelSerializer):
    get_item = serializers.ReadOnlyField()
    item_images = serializers.SerializerMethodField()

    class Meta:
        model = ItemTrending
        fields = '__all__'

    def get_item_images(self, obj):
        request = self.context.get('request')
        images = obj.get_item_images(request)
        return images


class ItemReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemReview
        fields = "__all__"


class ItemColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemColor
        fields = '__all__'


class ItemBrandNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemBrandName
        fields = '__all__'


class ItemBrandSerializer(serializers.ModelSerializer):
    brand_name = ItemBrandNameSerializer(many=False, read_only=True)

    class Meta:
        model = ItemBrand
        fields = '__all__'


class ItemSizeByModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemBrand
        fields = '__all__'


class ItemSizeByNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemBrand
        fields = '__all__'


class ItemColorChoiceSerializer(serializers.ModelSerializer):
    color = ItemColorSerializer(many=False, read_only=True)

    class Meta:
        model = ItemColorChoice
        fields = '__all__'


class ShippingChargeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingCharge
        fields = "__all__"


class AddressSerializer(CountryFieldMixin, serializers.ModelSerializer):
    country = CountryField()
    country_full = serializers.SerializerMethodField()

    class Meta:
        model = Address
        fields = "__all__"

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


class SimpleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = "__all__"


class ItemInstallmentDetailSerializer(serializers.ModelSerializer):
    item = SimpleItemSerializer()

    class Meta:
        model = ItemInstallmentDetail
        fields = "__all__"


class UserInstallmentPayDetailSerializer(serializers.ModelSerializer):
    installment_item = ItemInstallmentDetailSerializer(many=False, read_only=True)
    selected_shipping_charges = ShippingChargeSerializer(many=False, read_only=True)
    selected_address = AddressSerializer(many=False, read_only=True)
    next_payment_amount = serializers.SerializerMethodField()
    actual_remaining_balance = serializers.SerializerMethodField()
    actual_total = serializers.SerializerMethodField()
    addresses = serializers.SerializerMethodField()
    shipping_charges = serializers.SerializerMethodField()

    class Meta:
        model = UserInstallmentPayDetail
        fields = '__all__'

    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = _user(self.context['request'])
        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        """
        Override the create method to calculate the required_period, paid_for_period,
        next_amount_to_pay, and payment_due_date before saving the instance.
        """
        data = self.context['request'].data
        # Calculate the required_period, paid_for_period, next_amount_to_pay,
        # and payment_due_date based on the initial payment
        required_period = validated_data['required_period']
        paid_for_period = 1
        # Update the instance with the calculated values
        validated_data['required_period'] = required_period
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Override the update method to calculate the next_amount_to_pay and
        update the paid_for_period and payment_due_date based on the new amount_paid
        """
        if instance.completed:
            return super().update(instance, validated_data)

        amount_paid = validated_data.get("amount_paid", None)
        if amount_paid:
            # If its first time
            if instance.remaining_balance == 0:
                remaining_balance = float(instance.installment_item.total_cost) - (float(amount_paid) - float(instance.selected_shipping_charges.shipping_cost))
            # Not first time
            else:
                remaining_balance = float(instance.remaining_balance) - float(amount_paid)
            # Calculate the next_amount_to_pay based on the remaining_balance
            required_period = instance.required_period
            current_due_date = instance.payment_due_date
            periods_remaining = instance.paid_for_period
            required_period = instance.required_period
            next_days = datetime.timedelta(days=periods_remaining * 30)
            if instance.payment_due_date and instance.payment_due_date >= datetime.date.today():
                periods_remaining = 0
                next_days = 0
                # Meaning there are NO remaining periods, i.e. LESS than 1, then payment_due_date is today
            elif instance.payment_due_date and instance.payment_due_date < datetime.date.today():
                instance.payment_due_date = current_due_date
                if remaining_balance <= 0:
                    instance.paid_for_period = required_period

            if not instance.payment_due_date:
                instance.paid_for_period += 1
                periods_remaining = required_period - instance.paid_for_period

            # Meaning there are remaining periods, i.e. greater than 1
            if periods_remaining > 0:
                next_days = datetime.timedelta(days=periods_remaining * 30)
                next_amount_to_pay = remaining_balance / periods_remaining
                instance.next_amount_to_pay = next_amount_to_pay
                if instance.payment_due_date:
                    instance.payment_due_date = instance.payment_due_date + next_days
                    # + datetime.timedelta(days=instance.installment_item.payment_period * 30 )
                else:
                    instance.payment_due_date = datetime.date.today() + next_days

            instance.remaining_balance = remaining_balance

            if instance.remaining_balance <= 0:
                instance.paid_for_period = instance.required_period
                instance.completed = True
        return super().update(instance, validated_data)

    def get_next_payment_amount(self, instance):
        return instance.next_payment_amount

    def get_addresses(self, instance):
        user = _user(self.context['request'])
        if instance.user:
            user = User.objects.get(id=instance.user.id)
        qs = Address.objects.filter(user=user)
        data = AddressSerializer(qs, many=True)
        return data.data

    def get_shipping_charges(self, instance):
        qs = ShippingCharge.objects.filter(item=instance.installment_item.item)
        data = ShippingChargeSerializer(qs, many=True, read_only=True)
        return data.data

    def get_actual_remaining_balance(self, instance):
        return instance.get_remaining_balance

    def get_actual_total(self, instance):
        return instance.actual_total


#
# class UserInstallmentPayDetailSerializer1(serializers.ModelSerializer):
#     installment_item = ItemInstallmentDetailSerializer(many=False, read_only=True)
#     selected_shipping_charges = ShippingChargeSerializer(many=False, read_only=True)
#     selected_address = AddressSerializer(many=False, read_only=True)
#     next_payment_amount = serializers.SerializerMethodField()
#     actual_remaining_balance = serializers.SerializerMethodField()
#     actual_total = serializers.SerializerMethodField()
#     addresses = serializers.SerializerMethodField()
#     shipping_charges = serializers.SerializerMethodField()
#
#     class Meta:
#         model = UserInstallmentPayDetail
#         fields = "__all__"
#
#     def get_next_payment_amount(self, instance):
#         return 0.00  # instance.next_payment_amount
#
#     def get_addresses(self, instance):
#         user = _user(self.context['request'])
#         if instance.user:
#             user = User.objects.get(id=instance.user.id)
#         qs = Address.objects.filter(user=user)
#         data = AddressSerializer(qs, many=True)
#         return data.data
#
#     def get_shipping_charges(self, instance):
#         qs = ShippingCharge.objects.filter(item=instance.installment_item.item)
#         data = ShippingChargeSerializer(qs, many=True)
#         return data.data
#
#     def get_actual_remaining_balance(self, instance):
#         return instance.get_remaining_balance
#
#     def get_actual_total(self, instance):
#         return instance.actual_total
#
#     def create(self, validated_data):
#         """
#         Override the create method to calculate the required_period, paid_for_period,
#         next_amount_to_pay, and payment_due_date before saving the instance.
#         """
#         installment_item = validated_data['installment_item']
#         selected_shipping_charges = validated_data['selected_shipping_charges']
#         deposit_amount = installment_item.deposit_amount
#         shipping_cost = selected_shipping_charges.shipping_cost
#         required_amount = deposit_amount + shipping_cost
#
#         amount_paid = validated_data['amount_paid']
#         remaining_balance = required_amount - amount_paid
#
#         # Calculate the required_period, paid_for_period, next_amount_to_pay,
#         # and payment_due_date based on the initial payment
#         required_period = installment_item.payment_period
#         paid_for_period = 1
#         next_amount_to_pay = remaining_balance / (required_period - 1)
#         payment_due_date = validated_data['payment_due_date']
#
#         # Update the instance with the calculated values
#         validated_data['required_period'] = required_period
#         validated_data['paid_for_period'] = paid_for_period
#         validated_data['next_amount_to_pay'] = next_amount_to_pay
#         validated_data['payment_due_date'] = payment_due_date
#         return super().create(validated_data)
#
#     def update(self, instance, validated_data):
#         """
#         Override the update method to calculate the next_amount_to_pay and
#         update the paid_for_period and payment_due_date based on the new amount_paid
#         """
#         installment_item = instance.installment_item
#         deposit_amount = installment_item.deposit_amount
#         selected_shipping_charges = instance.selected_shipping_charges
#         shipping_cost = selected_shipping_charges.shipping_cost
#         required_amount = deposit_amount + shipping_cost
#
#         amount_paid = validated_data['amount_paid']
#         remaining_balance = instance.remaining_balance - amount_paid
#
#         # Calculate the next_amount_to_pay based on the remaining_balance
#         required_period = instance.required_period
#         periods_remaining = required_period - instance.paid_for_period
#         next_amount_to_pay = remaining_balance / periods_remaining
#
#         # Update the instance with the calculated values
#         instance.paid_for_period += 1
#         instance.next_amount_to_pay = next_amount_to_pay
#         instance.payment_due_date = instance.payment_due_date + datetime.timedelta(
#             days=instance.installment_item.payment_period
#         )
#         instance.remaining_balance = remaining_balance
#
#         return super().update(instance, validated_data)


class ItemManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemManufacturer
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super(ItemSerializer, self).__init__(*args, **kwargs)
        self.related_dbs = {
            'ItemSizeByMode': ItemSizeByModeSerializer,
            'ItemSizeByNumber': ItemSizeByNumberSerializer,
            'ItemColor': ItemColorSerializer,
            'ItemColorChoice': ItemColorChoiceSerializer,
            'ItemBrand': ItemBrandSerializer,
        }

    reviews = ItemReviewSerializer(many=True, read_only=False)
    item_images = ItemImagesSerializer(many=True, read_only=False)
    related_db = GenericForeignKeyModelSerializer(many=True)
    manufacturer = ItemManufacturerSerializer(many=False, read_only=True)
    installments = serializers.SerializerMethodField()
    brand_name = serializers.SerializerMethodField()
    user_installment_pay_details = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    cart_count = serializers.SerializerMethodField()
    available_colors = serializers.SerializerMethodField()
    all_ratings = serializers.SerializerMethodField()
    item_rates = serializers.SerializerMethodField()
    category_name = serializers.ReadOnlyField()
    main_category_name = serializers.ReadOnlyField()
    delete_from_cart_url = serializers.URLField(source='get_delete_from_cart_url', read_only=True)
    reduce_qty_url = serializers.URLField(source='get_reduce_qty_url', read_only=True)
    add_qty_url = serializers.URLField(source='get_add_qty_url', read_only=True)

    class Meta:
        model = Item
        fields = '__all__'

    def to_representation(self, instance):
        # cache_key = f'related_db_{instance.pk}'
        # cached_data = cache.get(cache_key)
        # if cached_data:
        #     return cached_data
        data = super().to_representation(instance)
        self.update_related_db(instance)
        data = self.serialize_related_db(data, instance)
        # cache.set(cache_key, data, timeout=3600)
        return data

    def check_related_db(self, name):
        try:
            return self.related_dbs[name]
        except KeyError:
            return None

    def update_related_db(self, instance):
        related_dbs = instance.related_db.all()
        related_dbs_type = set(db.db_type for db in instance.db_type.all())
        related_dbs_db_type = set(db.db_type for db in related_dbs)
        if related_dbs_type != related_dbs_db_type:
            if "NE" in related_dbs_type:
                instance.related_db.set(GenericForeignKeyModel.objects.none())
            else:
                related_objects = GenericForeignKeyModel.objects.filter(db_type__in=list(related_dbs_type))
                instance.related_db.set(related_objects)
            instance.save()
            print(instance.related_db.all())

    def serialize_related_db(self, data, instance):
        related_dbs_qs = instance.related_db.all()  # .prefetch_related('content_type')
        if related_dbs_qs.exists():
            for db in related_dbs_qs:
                db_ = db.content_type.model_class()
                try:
                    serializer_cls = self.related_dbs[db_.__name__]
                    if serializer_cls.__name__ == "ItemColorChoiceSerializer":
                        qs = ItemColorChoice.objects.filter(item=instance)
                        values = serializer_cls(qs, many=True).data
                        data['options_color'] = values
                    elif serializer_cls.__name__ == "ItemSizeByModeSerializer":
                        data['options_sizes'] = ItemSizeByMode.SIZE_CHOICES
                    elif serializer_cls.__name__ == "ItemSizeByNumberSerializer":
                        data['options_sizes'] = ItemSizeByNumber.SIZE_CHOICES
                    elif serializer_cls.__name__ == "ItemBrandSerializer":
                        qs = ItemBrand.objects.filter(item=instance)
                        data['options_brands'] = ItemBrandSerializer(qs, many=True).data
                except KeyError:
                    continue
                except Exception as e:
                    continue
        return data

    def get_available_colors(self, obj):
        qs = obj.available_colors.all()
        data = ItemColorSerializer(qs, many=True).data
        return data

    def get_label(self, obj):
        req = self.context
        return obj.get_label_display()

    def get_cart_count(self, obj):
        item_in_cart = obj.in_cart.all().filter(item=obj, ordered=False)
        if item_in_cart.exists():
            return item_in_cart[0].quantity

    def get_add_to_cart_url(self, obj):
        obj_url = obj.get_add_to_cart_url()
        return self.context["request"].build_absolute_uri(obj_url)

    def get_installments(self, obj):
        data = None
        if not obj.pay_with_installment:
            return data
        qs = ItemInstallmentDetail.objects.filter(item=obj)
        data = ItemInstallmentDetailSerializer(qs, many=True).data
        return data

    # except Exception as e:
    # return None
    def get_user_installment_pay_details(self, obj):
        if not obj.pay_with_installment:
            return None
        user = _user(self.context['request'])
        if user and user.is_authenticated:
            return None
        item_installment_detail = ItemInstallmentDetail.objects.select_related('item').filter(item=obj).first()
        if not item_installment_detail:
            return None
        item_title = item_installment_detail.item.title
        try:
            qs = UserInstallmentPayDetail.objects.filter(
                user=user,
                installment_item__item__title=item_title,
                amount_paid=None
            ).earliest('created_at')
            if qs:
                data = UserInstallmentPayDetailSerializer(qs, many=False, context=self.context).data
                return data
        except UserInstallmentPayDetail.DoesNotExist:
            return None
        return None

    def get_brand_name(self, obj):
        qs = ItemBrand.objects.filter(item=obj)
        if qs.exists():
            serializer = ItemBrandSerializer(instance=qs.first(), many=False, context=self.context)
            return serializer.data
        return None

    def get_all_ratings(self, obj):
        return obj.get_ratings

    def get_item_rates(self, obj):
        return ITEM_RATINGS


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = "__all__"

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


class TownLocationSerializer(serializers.Serializer):
    town = serializers.CharField()
    locations = ShippingLocationChargesSerializer(many=True)


# "start_date","ordered_date","ordered","shipping_address","billing_address",
# "payment","coupon","being_delivered","received","refund_requested","refund_granted","ref_code",
class OrderSerializer(serializers.ModelSerializer):
    shipping_options = serializers.SerializerMethodField()
    items = CartItemSerializer(read_only=False, many=True)
    order_total = serializers.SerializerMethodField()
    total_discount = serializers.SerializerMethodField()
    coupon = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    payment = serializers.SerializerMethodField()
    ref_code = serializers.SerializerMethodField()
    ordered = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()

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

    def get_total_items(self, obj):
        return obj.items.all().count()

    def get_shipping_options(self, obj):
        towns = ShippingLocationCharges.objects.values('town__name').distinct()
        towns_data = [{'town': town['town__name'],
                       'locations': list(ShippingLocationCharges.objects.by_town(town['town__name']))} for town in towns]
        serializer = TownLocationSerializer(towns_data, many=True)
        return serializer.data

    #
    # def to_representation(self, instance):
    #     """
    #             This is to_represent method in ItemSerializer, of Item Model.
    #             related_db field which ManyToManyField in Item model is populated with GenericForeignKeyModel model instances.
    #             Both Item model and GenericForeignKeyModel model have a choice field called db_type,
    #             and they use the same tuple called DB_TYPES as choice options.
    #             Here, we compare if db_type field in Item model which returns a list of DB_TYPES and related_db field instances
    #             if they have same list of DB_TYPES options and if not we alter related_db field, save and then update field.
    #     """
    #     data = super().to_representation(instance)
    #     related_dbs = instance.related_db.all()
    #     related_dbs_type = set(instance.db_type)
    #     related_dbs_db_type = set(db.db_type for db in related_dbs)
    #
    #     if related_dbs_type != related_dbs_db_type:
    #         # If NONE was selected in db_type in Item model, then set related_db to empty qs
    #         if "NE" in related_dbs_type:
    #             instance.related_db.set(GenericForeignKeyModel.objects.none())
    #         else:
    #             # Otherwise save add all GenericForeignKeyModel objects with the same db_type
    #             related_objects = GenericForeignKeyModel.objects.filter(db_type__in=list(instance.db_type))
    #             instance.related_db.set(related_objects)
    #         instance.save()
    #     if related_dbs.exists():
    #         # If this Item Instance have related_db then dynamically add the fields base on related model
    #         # stored in related_dbs
    #         for db in instance.related_db.all():
    #             # for loop is expensive operations
    #             db_ = db.content_type.model_class()
    #             # Get serializer class stored in  self.related_dbs = {'ItemSizeByMode': ItemSizeByModeSerializer,
    #             #                             'ItemBrand': ItemBrandSerializer, }
    #             serializer_cls = self.check_related_db(db_.__name__)
    #             # Compare class names to get the correct Serializer class
    #             # Carryout logic checks and inject extra fields
    #             if serializer_cls.__name__ == "ItemColorChoiceSerializer":
    #                 qs = ItemColorChoice.objects.filter(item=instance)
    #                 values = serializer_cls(qs, many=True).data
    #                 data['color_options'] = values
    #             elif serializer_cls.__name__ == "ItemSizeByModeSerializer":
    #                 # To ensure that SIZE_CHOICES is present
    #                 data['size_choices'] = ItemSizeByMode.SIZE_CHOICES
    #             elif serializer_cls.__name__ == "ItemSizeByNumberSerializer":
    #                 data['size_choices'] = ItemSizeByNumber.SIZE_CHOICES
    #             elif serializer_cls.__name__ == "ItemBrandSerializer":
    #                 qs = ItemBrand.objects.filter(item=instance)
    #                 data['brand_options'] = ItemBrandSerializer(qs, many=True).data
    #     return data

# def serialize_related_db1(data, instance):
#     related_dbs = instance.related_db.all()
#     related_dbs_dict = {
#         'ItemSizeByMode': ItemSizeByModeSerializer,
#         'ItemSizeByNumber': ItemSizeByNumberSerializer,
#         'ItemColor': ItemColorSerializer,
#         'ItemColorChoice': ItemColorChoiceSerializer,
#         'ItemBrand': ItemBrandSerializer,
#     }
#     if related_dbs.exists():
#         for db in related_dbs:
#             # for loop is expensive operations
#             db_ = db.content_type.model_class()
#             try:
#                 serializer_cls = related_dbs_dict[db_.__name__]
#             except KeyError:
#                 continue
#             if serializer_cls.__name__ == "ItemColorChoiceSerializer":
#                 qs = ItemColorChoice.objects.filter(item=instance)
#                 values = serializer_cls(qs, many=True).data
#                 data['color_options'] = values
#             elif serializer_cls.__name__ == "ItemSizeByModeSerializer":
#                 data['size_choices'] = ItemSizeByMode.SIZE_CHOICES
#             elif serializer_cls.__name__ == "ItemSizeByNumberSerializer":
#                 data['size_choices'] = ItemSizeByNumber.SIZE_CHOICES
#             elif serializer_cls.__name__ == "ItemBrandSerializer":
#                 qs = ItemBrand.objects.filter(item=instance)
#                 data['brand_options'] = ItemBrandSerializer(qs, many=True).data
#     return data
#
