# Create your views here.
import random
import string

import requests
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, permissions, generics
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from api_auth.registration.serializers import RegisterSerializer
from core.methods import _user
from shop.models import *
from . import serializers as s

from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from phonenumber_field.validators import validate_international_phonenumber
from django.forms.models import model_to_dict


class PhoneSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(validators=[validate_international_phonenumber])


def validate_phone_number(phone_number):
    serializer = PhoneSerializer(data={"phone_number": phone_number})
    if serializer.is_valid():
        return phone_number
    else:
        print(serializer.errors)
        return None


channel_layer = get_channel_layer()

User = get_user_model()


def create_ref_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '' or None:
            valid = False
    return valid


def get_item_in_order(slug, request):
    """
    The get_item_in_order function is a helper function that takes in two arguments: slug and request.
    It returns an order_item object if the item is already in the user's cart, or None otherwise.
    :param slug: Get the item with that slug
    :param request: Get the user's information
    :return: The order_item object
    """
    item = get_object_or_404(Item, slug=slug)
    user = request.user
    order_qs = Order.objects.filter(user=user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = CartItem.objects.filter(
                item=item, user=user, ordered=False
            )[0]
            return order_item
        else:
            return None
    return None


class ItemsCategoriesListAPIView(ListAPIView):
    model = ItemCategory
    serializer_class = s.ItemCategorySerializer
    permission_classes = [permissions.AllowAny, ]
    queryset = ItemCategory.objects.all()


class TrendingItemsListAPIView(APIView):
    serializer_class = s.ItemTrendingSerializer
    permission_classes = [permissions.AllowAny, ]

    def get(self, *args, **kwargs):
        queryset = ItemTrending.objects.all()
        serializer = self.serializer_class(queryset, many=True, context={"request": self.request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# Fake api of products
@method_decorator(csrf_exempt, name="dispatch")
class AutoCreateProducts(APIView):
    permission_classes = [permissions.AllowAny, ]

    def post(self, request, Format=None, *args, **kwargs) -> HttpResponse:
        queryset = Item.objects.all()
        import random
        if not (queryset.count() > 19):
            req = requests.get('https://fakestoreapi.com/products')
            for item in req.json():
                item = Item(
                    title=item["title"],
                    price=item["price"],
                    category=item["category"],
                    description=item["description"],
                    image=item["image"],
                    stock=random.randint(1, 89),
                    rating_count=item["rating"]['count'],
                    rates=item["rating"]['rate'],
                )
                item.save()
        serializer = s.ItemSerializer(queryset, many=True, context={"request": request})
        return Response({
            "items": serializer.data,
        }, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class ItemDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = s.ItemSerializer
    lookup_field = "slug"

    def get_object(self):
        try:
            item = Item.objects.get(slug=self.kwargs["slug"])
            return item
        except ObjectDoesNotExist:
            return None


@method_decorator(csrf_exempt, name="dispatch")
class AddressAPIView(generics.ListAPIView):
    permissions_classes = [permissions.AllowAny, ]
    queryset = Address.objects.all()
    serializer_class = s.AddressSerializer


@method_decorator(csrf_exempt, name="dispatch")
class ItemsAPIView(APIView):
    """
    A view that returns a list of all items in the database.
    """
    permission_classes = [permissions.AllowAny]
    # queryset =
    serializer_class = s.ItemSerializer

    def get(self, *args, **kwargs):
        qs = Item.objects.all()
        serializer = s.ItemSerializer(qs, many=True, context={"request": self.request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# REQUIRE AUTHENTICATION
# @method_decorator(csrf_protect, name="dispatch")
@method_decorator(csrf_exempt, name="dispatch")
class AddToCartAPIView(APIView):
    """Adding to cart API"""
    permission_classes = [permissions.AllowAny]
    order_serializer = s.OrderSerializer
    item_serializer = s.ItemSerializer

    def post(self, request, *args, **kwargs) -> HttpResponse:

        slug = request.data.get("slug", None) or kwargs.get('slug', None)
        quantity = request.data.get("quantity", None) or kwargs.get('quantity', None)
        color = request.data.get("color", None) or kwargs.get('color', None)
        size = request.data.get("size", None) or kwargs.get('size', None)
        describe = request.data.get("describe", None) or kwargs.get('describe', None)
        user = _user(request)
        try:
            stock = int(quantity)
        except ValueError:
            stock = 1
        except Exception as e:
            stock = 1
        if slug is None:
            return Response({"details": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

        item = get_object_or_404(Item, slug=slug)
        item.stock -= stock
        item.save()
        order_item, created = CartItem.objects.get_or_create(
            item=item,
            user=user,
            ordered=False,
            describe=describe,
            chosen_color=color,
            chosen_size=size
        )

        order_qs = Order.objects.filter(user=user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if order.items.filter(item__slug=item.slug).exists():
                order_item.quantity += 1
                order_item.save()
            else:
                order_item.quantity = stock
                order.items.add(order_item)
            return Response({
                "details": f"{item.title} quantity updated",
                "item": self.item_serializer(item, context={"request": request}).data,
                "order": self.order_serializer(order, context={"request": request}).data,
                "items": s.ItemSerializer(Item.objects.all(), many=True, context={"request": request}).data,
            }, status=status.HTTP_200_OK)
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(user=user, ordered_date=ordered_date, ref_code=create_ref_code())
            order_item.quantity = stock
            order_item.save()
            order.items.add(order_item)
            return Response({
                "details": f"{item.title} added to your cart",
                "item": self.item_serializer(item, context={"request": request}).data,
                "order": self.order_serializer(order, context={"request": request}).data,
                "items": s.ItemSerializer(Item.objects.all(), many=True, context={"request": request}).data,
            }, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class DeleteItemFromCartView(APIView):
    """
    - Api that provide functionality to delete item from the cart
    - User must be authenticated
    """
    permission_classes = [permissions.AllowAny, ]

    def post(self, request, format=None, *args, **kwargs):
        user = _user(request)
        slug = request.data.get("slug", None) or kwargs.get('slug', None)
        if slug is None:
            return Response(
                {"details": "Invalid request"}, status=status.HTTP_200_OK
            )
        item = get_object_or_404(Item, slug=slug)
        order_qs = Order.objects.filter(user=user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if order.items.filter(item__slug=item.slug).exists():
                try:
                    order_item = CartItem.objects.get(item=item)
                except MultipleObjectsReturned:
                    order_item = CartItem.objects.filter(item=item)[0]
                order.items.remove(order_item)
                item.stock += order_item.quantity
                item.save()
                order_item.delete()
                # check if order has items if no delete the order
                order_response = None
                if not order.items.all().exists():
                    order.delete()
                else:
                    order_response = s.OrderSerializer(order, context={"request": request}).data
                return Response(
                    {
                        "details": f"{item.title} - removed from your cart.",
                        "item": s.ItemSerializer(item, context={'request': request}).data,
                        "order": order_response,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "details": "This item was not in your cart",
                        "item": s.ItemSerializer(item, context={'request': request}).data,
                        "order": s.OrderSerializer(order, context={"request": request}).data,
                    },
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                {
                    "details": "You do not have an active order",
                    "item": s.ItemSerializer(item, context={'request': request}).data,
                    "order": None,
                },
                status=status.HTTP_200_OK,
            )


@method_decorator(csrf_exempt, name="dispatch")
class ReduceItemQuantityView(APIView):
    """
    - Api that provide functionality to reduce item from the cart by 1
    - User must be authenticated
    """
    permission_classes = [permissions.AllowAny, ]

    def post(self, request, format=None, *args, **kwargs):
        slug = request.data.get("slug", None) or kwargs.get('slug', None)
        user = _user(request)
        response_obj = {}
        if slug is None:
            return Response({"details": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        item = get_object_or_404(Item, slug=slug)
        order_qs = Order.objects.filter(user=user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if order.items.filter(item__slug=item.slug).exists():
                order_item = CartItem.objects.filter(
                    item=item, user=user, ordered=False
                )[0]
                if order_item.quantity > 1:
                    order_item.quantity -= 1
                    item.stock += 1
                    item.save()
                    order_item.save()
                    response_obj["details"] = "Item quantity updated."
                    response_obj["item"] = s.ItemSerializer(item, context={'request': request}).data
                    response_obj["order"] = s.OrderSerializer(order, context={"request": request}).data
                    return Response(response_obj, status=status.HTTP_200_OK)
                else:
                    item.stock += order_item.quantity
                    item.save()
                    order_item.delete()
                    response_obj["order"] = s.OrderSerializer(order, context={"request": request}).data
                    response_obj["item"] = {}
                    response_obj["details"] = "Item removed from cart"
                    if not order.items.count() > 0:
                        order.delete()
                        response_obj["details"] = "Your cart is empty"
                        response_obj["order"] = None
                    return Response(response_obj, status=status.HTTP_200_OK)

            else:
                response_obj["order"] = s.OrderSerializer(order, context={"request": request}).data
                response_obj["item"] = s.ItemSerializer(item, context={'request': request}).data
                response_obj["details"] = "This item is not in your cart"
                return Response(response_obj, status=status.HTTP_200_OK)
        else:
            response_obj["order"] = None
            response_obj["item"] = s.ItemSerializer(item, context={'request': request}).data
            response_obj["details"] = "You do not have an active order"
            return Response(response_obj, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class AddItemQuantityAPIView(APIView):
    permission_classes = [permissions.AllowAny, ]

    def post(self, request, format=None, *args, **kwargs):
        slug = self.request.data.get("slug", None) or kwargs.get('slug', None)
        user = _user(request)
        if slug is None:
            return Response({"details": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        item = get_object_or_404(Item, slug=slug)
        order_qs = Order.objects.filter(user=user, ordered=False)
        try:
            assert order_qs.exists(), "No active order!"
            order = order_qs.first()
            try:
                assert order.items.filter(item__slug=item.slug).exists(), "Item not in cart"
                order_item = CartItem.objects.filter(item=item, user=user, ordered=False).first()
                order_item.quantity += 1
                item.stock -= 1
                item.save()
                order_item.save()
                return Response({
                    "details": "Item quantity updated.",
                    "item": s.ItemSerializer(item, context={'request': request}).data,
                    "order": s.OrderSerializer(order, context={"request": request}).data,
                }, status=status.HTTP_200_OK)
            except AssertionError:
                return Response({
                    "details": "This item is not in your cart",
                    "item": s.ItemSerializer(item, context={'request': request}).data,
                    "order": s.OrderSerializer(order, context={"request": request}).data,
                }, status=status.HTTP_200_OK)
        except AssertionError:
            return Response({
                "details": "You do not have an active order",
                "item": s.ItemSerializer(item, context={'request': request}).data,
                "order": None,
            }, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class OrderDetailView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = s.OrderSerializer

    def get(self, *args, **kwargs):
        user = _user(self.request)
        if user.is_authenticated:
            try:
                order = Order.objects.get(user=user, ordered=False)
            except MultipleObjectsReturned:
                order = Order.objects.filter(user=user, ordered=False)[0]
            except ObjectDoesNotExist:
                order = None
                return Response(None, status=status.HTTP_200_OK)
            return Response(self.serializer_class(order, many=False, context={'request': self.request}).data,
                            status=status.HTTP_200_OK)
        return Response({"order": None}, status=status.HTTP_200_OK)

    def post(self, *args, **kwargs):
        ref_code = self.request.data.get('ref_code', None)
        if not ref_code:
            return Response(None, status=status.HTTP_200_OK)
        try:
            order = Order.objects.get(ref_code=ref_code)
        except ObjectDoesNotExist:
            return Response(None, status=status.HTTP_200_OK)
        return Response(self.serializer_class(order, many=False, context={'request': self.request}).data,
                        status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class CompletedOrderView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = s.OrderSerializer

    def get_queryset(self):
        user = _user(self.request)
        order = Order.objects.filter(user=user, ordered=True)
        return order


@method_decorator(csrf_exempt, name="dispatch")
class AddCouponView(APIView):
    """
    - Api that adds a coupon to the  order and reduces the amount charged with the value of the coupon
    - User must be authenticated
    """
    permission_classes = [permissions.AllowAny, ]

    def post(self, request, format=None, *args, **kwargs):
        user = _user(request)
        code = request.data.get("code")
        if code is None:
            return Response(
                {"details": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST
            )
        order = Order.objects.get(user=user, ordered=False)
        coupon = None
        try:
            coupon = Coupon.objects.get(code=code, redeemed=False)
        except Coupon.DoesNotExist:
            return Response(
                {"details": "That coupon has expired or doesn't exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        coupon.redeemed = True
        coupon.save()
        order.coupon = coupon
        order.save()
        return Response(
            {
                "details": "Successfully added coupon",
                "order": s.OrderSerializer(order, context={"request": request}).data,
            }, status=status.HTTP_200_OK
        )


@method_decorator(csrf_exempt, name="dispatch")
class RetrieveAddress(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None, *args, **kwargs):
        user = _user(request)
        try:
            address = Address.objects.filter(user=user)
            return Response({
                "address": s.AddressSerializer(address, many=True).data,
                "details": "You have one previous address. You can update it.",
            },
                status=status.HTTP_200_OK
            )
        except ObjectDoesNotExist:
            return Response(
                {"details": "Fill the form with shipping details", "address": None}, status=status.HTTP_200_OK
            )


@method_decorator(csrf_exempt, name="dispatch")
class CreateAddressView(APIView):
    permission_classes = [permissions.AllowAny, ]
    serializer_class = s.AddressSerializer

    def get_order(self, user):
        try:
            order = Order.objects.get(user=user, ordered=False)
        except Order.DoesNotExist:
            return Response({"details": "You do not have an active order"}, status=status.HTTP_200_OK)
        return order

    def get_shipping_address(self, addr_id):
        try:
            addr = Address.objects.get(id=addr_id)
            return addr
        except Address.DoesNotExist:
            return Response({
                "details": "That address could not be used. Try updating it",
                "redirect": False}, status=status.HTTP_404_NOT_FOUND, )

    def create_address(self, request):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        order = self.get_order(_user(request))
        if serializer.is_valid():
            serializer.save()
            return Response({
                "details": "Address updated successfully",
                "address": serializer.data,
                "order": s.OrderSerializer(order, context={"request": request}).data,
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "details": serializer.errors,
                "address": None,
                "order": None,
            }, status=status.HTTP_400_BAD_REQUEST)

    def use_current_address(self, request):
        addr_id = request.data.get("id", None)
        order = self.get_order(_user(request))
        addr = self.get_shipping_address(addr_id)
        order.billing_address = addr
        # Manually setting shipping address as billing address
        order.shipping_address = addr
        order.save()
        return Response({
            "details": "Address set successfully",
            "redirect": True,
            "order": s.OrderSerializer(order, context={"request": request}).data,
        },
            status=status.HTTP_200_OK)

    def post(self, request, format=None, *args, **kwargs):
        use_current = request.data.get("useCurrent", None)
        if use_current:
            return self.use_current_address(request)
        return self.create_address(request)


@method_decorator(csrf_exempt, name="dispatch")
class CrudShippingAddrView(APIView):
    permission_classes = [permissions.AllowAny, ]

    def get_address(self, *args, **kwargs):
        user = _user(self.request)
        try:
            address = Address.objects.by_user(user)
        except ObjectDoesNotExist:
            address = None
        return address

    def post(self, *args, **kwargs):
        data = self.request.data
        address = None
        update = data.get("update", None)
        to_update = data.get("to_update", None)
        delete = data.get("delete", None)
        address_id = data.get("id", None)
        if address_id:
            address = Address.objects.get(id=data['id'])
        create = data.get("create", None)
        if update:
            for add in self.get_address().all():
                if add is address:
                    continue
                else:
                    add._default = False
                    add.save()
            serializer = s.AddressSerializer(instance=address, data=data, many=False, partial=True,
                                             context={'request': self.request})
            if serializer.is_valid():
                serializer.save()
                serialized_addrs = s.AddressSerializer(self.get_address(), many=True)
                response_obj = {
                    'default': True,
                    "update_success": "Address has been updated.",
                    "address": serialized_addrs.data
                }
                if not to_update:
                    response_obj['default'] = True
                return Response(response_obj, status=status.HTTP_200_OK)
        if delete:
            address.delete()
            serialized_addrs = s.AddressSerializer(self.get_address(), many=True)
            return Response({
                "delete": True,
                "update_success": "Address deleted.",
                "address": serialized_addrs.data
            }, status=status.HTTP_200_OK)
        if create:
            serializer = s.AddressSerializer(initial={'country': 'KE'}, data=data, many=False,
                                             context={'request': self.request})
            if serializer.is_valid():
                serializer.save()
                serialized_addrs = s.AddressSerializer(self.get_address(), many=True)
                return Response({
                    "create": True,
                    "update_success": "Address created.",
                    "address": serialized_addrs.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({"create_error": serializer.errors}, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class MpesaPay(APIView):
    permission_classes = [permissions.AllowAny, ]

    def post(self, request, format=None, *args, **kwargs):
        print(request.data)
        pay_id = request.data.get("pay_id")
        amount = request.data.get("amount")
        shipping_charge = request.data.get("shipping_charge")
        user = _user(request)
        try:
            shipping_charges = ShippingLocationCharges.objects.get(id=shipping_charge)
        except ShippingLocationCharges.DoesNotExist:
            return Response({'detail': "Wrong shipping charge received."}, status=status.HTTP_400_BAD_REQUEST)
        mpesa_no = validate_phone_number(request.data["mpesa_number"])
        if not mpesa_no:
            return Response({'detail': "Enter a valid phone number format."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = Order.objects.get(user=user, ordered=False)
        except Order.DoesNotExist:
            return Response({'detail': "Order payment was done"}, status=status.HTTP_400_BAD_REQUEST)
        total = order.get_total
        if amount < total:
            return Response({'detail': "Amount discrepancy. Payment failed"}, status=status.HTTP_400_BAD_REQUEST)
        amount_shipping = shipping_charges.charge_per_kg
        order.shipping_charges = shipping_charges
        order_items = order.items.all()
        order_items.update(ordered=True)
        for item in order_items:
            qty = item.quantity
            if item.item.stock >= qty:
                # TODO: calculate the amount of Kgs of item and get the actual shipping charges
                # TODO: And this should be done in the save method to give user accurate amount before paying.
                item.item.stock -= qty
            item.item.save()
            item.save()

        payment = Payment.objects.create(
            user=user,
            stripe_charge_id=pay_id,
            amount=amount + amount_shipping,
            mpesa_no=mpesa_no
        )
        order.payment = payment
        order.ordered = True
        order.save()
        return Response({
            "order": s.OrderSerializer(order, context={"request": request}).data,
            'detail': "Successfully transacted through Mpesa"
        }, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class PurchaseWithInstallMentAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, format=None, *args, **kwargs):
        return Response(self.request.data, status=status.HTTP_200_OK)

    def post(self, format=None, *args, **kwargs):
        item_id = self.request.data['item']["id"]
        payment_period = self.request.data['payment_period']
        installment_obj = ItemInstallmentDetail.objects.select_related('item').get(id=self.request.data['id'])
        user = _user(self.request)
        # Try to get all UserInstallmentPayDetail without amount_paid, with (same item)
        # installment_item.item.id is item_id
        user_payment_detail = UserInstallmentPayDetail.objects.filter(
            Q(amount_paid=None) | Q(amount_paid=0),
            user=user,
            installment_item__item_id=item_id,
        )
        # If it exists, either many or one
        if user_payment_detail.exists():
            # Filter with period and get the one that matches the period
            response = user_payment_detail.filter(installment_item__payment_period=payment_period)
            if response.exists():
                # If that exists, delete the rest with different payment periods say 1, 3, 4 e.t.c excluding 2
                # Return that with payment period of 2, which is payment_detail above, otherwise we have nothing
                # to delete
                user_payment_detail.exclude(pk__in=response).delete()
                response = response[0]
            else:
                response = self.create_user_installment_detail(installment_obj)
                user_payment_detail.exclude(pk=response.id).delete()
        else:
            # If we don't have any user_payment_detail with item (meaning it's new in the existing qs)
            # we create one with user=user, item_installment_id=item_installment_id
            response = self.create_user_installment_detail(installment_obj)
        data = s.UserInstallmentPayDetailSerializer(instance=response, many=False, context={'request': self.request}).data
        return Response(data, status=status.HTTP_200_OK)

    def create_user_installment_detail(self, installment_obj):
        user = _user(self.request)
        return UserInstallmentPayDetail.objects.create(
            user=user,
            installment_item=installment_obj,
            required_period=installment_obj.payment_period
        )


@method_decorator(csrf_exempt, name="dispatch")
class PurchaseInstallMentProfileAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None, *args, **kwargs):
        try:
            instance = UserInstallmentPayDetail.objects.get(pk=request.data['id'])
        except UserInstallmentPayDetail.DoesNotExist:
            return Response({
                'detail': f'Purchase profile does not exist. Probably deleted.'
            }, status=status.HTTP_400_BAD_REQUEST)
        data = s.UserInstallmentPayDetailSerializer(instance=instance, many=False, context={'request': self.request}).data
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, format=None, *args, **kwargs):
        profile_id = request.data.get('profile_id', None)
        profile = get_object_or_404(UserInstallmentPayDetail, pk=profile_id)
        data = request.data
        updated = False  # flag to track if the profile has been updated

        if data.get('selected_shipping_charges', None) is not None:
            profile.selected_shipping_charges = ShippingCharge.objects.get(id=data['id'])
            updated = True
        if data.get('address', None) is not None and data.get('create_address', None) is None:
            profile.selected_address = Address.objects.get(id=data['id'])
            updated = True
        if data.get('mpesa', None) is not None:
            profile.mpesa_no = data['mpesa_no']
            updated = True
        if data.get('create_address', None) is not None:
            del data['create_address']
            del data['profile_id']
            data['user'] = _user(request)
            addr = Address.objects.create(**data)
            profile.selected_address = addr
            updated = True

        if updated:
            profile.save()
            data = s.UserInstallmentPayDetailSerializer(
                instance=profile,
                many=False,
                context={'request': self.request}
            ).data
            return Response(data, status=status.HTTP_200_OK)
        return Response({'details': "Failed to update purchase profile"}, status=status.HTTP_400_BAD_REQUEST)

    # def put(self, request, format=None, *args, **kwargs):
    #     profile_id = request.data.get('profile_id', None)
    #     profile = get_object_or_404(UserInstallmentPayDetail, pk=profile_id)
    #     data = request.data
    #     if data.get('selected_shipping_charges', None) is not None:
    #         profile.selected_shipping_charges = ShippingCharge.objects.get(id=data['id'])
    #         profile.save()
    #         data = s.UserInstallmentPayDetailSerializer(instance=profile, many=False, context={'request': self.request}).data
    #     if data.get('address', None) is not None and data.get('create_address', None) is None:
    #         profile.selected_address = Address.objects.get(id=data['id'])
    #         profile.save()
    #         data = s.UserInstallmentPayDetailSerializer(instance=profile, many=False, context={'request': self.request}).data
    #     if data.get('mpesa', None) is not None:
    #         profile.mpesa_no = data['mpesa_no']
    #         profile.save()
    #         data = s.UserInstallmentPayDetailSerializer(instance=profile, many=False, context={'request': self.request}).data
    #     if data.get('create_address', None) is not None:
    #         del data['create_address']
    #         del data['profile_id']
    #         addr = Address.objects.create(**data)
    #         profile.selected_address = addr
    #         profile.save()
    #         data = s.UserInstallmentPayDetailSerializer(instance=profile, many=False, context={'request': self.request}).data
    #     return Response(data, status=status.HTTP_200_OK)


# from datetime import timedelta
# from rest_framework import status
from rest_framework.generics import CreateAPIView


# from rest_framework.response import Response
# from myapp.models import ItemInstallmentDetail, UserInstallmentPayDetail
@method_decorator(csrf_exempt, name="dispatch")
class CompleteInstallmentPayAPIView(APIView):
    permission_classes = [permissions.AllowAny, ]

    def post(self, format=None, *args, **kwargs):
        data = self.request.data
        shipping = data.get("selected_shipping_charges", None)
        next_pay = data.get("next_payment_amount", None)

        # Getting the current UserInstallmentPayDetail using id
        purchase_profile = get_object_or_404(UserInstallmentPayDetail, id=data.get('id', None))
        if purchase_profile.completed:
            return self.payment_completed()

        # TODO: Make payment through MPESA API and return the amount paid
        # The amount (mpesa_pay_amount) should be received from MPESA API Endpoint
        mpesa_pay_amount = data.get('mpesa_pay_amount')

        # Calculate the remaining balance, taking into account the shipping charges
        remaining_balance = purchase_profile.installment_item.total_cost - purchase_profile.amount_paid - float(shipping["shipping_cost"])

        # If the amount paid is less than the required deposit + shipping charge, return an error response
        if not purchase_profile.payment_due_date or purchase_profile.payment_due_date is None:
            deposit = float(purchase_profile.installment_item.deposit_amount)
            if mpesa_pay_amount < (deposit + remaining_balance):
                return self.less_amount_paid(mpesa_pay_amount, deposit)

        # Update the amount paid and remaining balance
        previous_amount = purchase_profile.amount_paid
        purchase_profile.amount_paid += mpesa_pay_amount
        purchase_profile.remaining_balance = remaining_balance

        # Update the payment_due_date and next_amount_to_pay
        if not purchase_profile.payment_due_date or purchase_profile.payment_due_date is None:
            purchase_profile.payment_due_date = timezone.now() + purchase_profile.installment_item.payment_period
        purchase_profile.next_amount_to_pay = max(remaining_balance, float(next_pay or 0))

        # If the amount paid and shipping charges sum up to the total cost, mark the payment as completed
        if float(purchase_profile.amount_paid) + float(shipping["shipping_cost"]) >= purchase_profile.installment_item.total_cost:
            purchase_profile.completed = True

        # Save the installment payment detail
        purchase_profile.save()

        serializer = s.UserInstallmentPayDetailSerializer(
            purchase_profile,
            many=False,
            context={'request': self.request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def less_amount_paid(self, amount, deposit):
        return Response({
            'detail': f'The amount received ({amount}) is less than the REQUIRED deposit ({deposit})'
        }, status=status.HTTP_400_BAD_REQUEST)

    def payment_completed(self):
        return Response({
            'detail': "This order payment was completed."
        }, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class CompleteInstallmentPayAPIVie(APIView):
    permission_classes = [permissions.AllowAny, ]

    def post(self, format=None, *args, **kwargs):
        data = self.request.data
        shipping = data.get("selected_shipping_charges", None)
        next_pay = data.get("next_payment_amount", None)

        # Getting the current UserInstallmentPayDetail using id
        purchase_profile = get_object_or_404(UserInstallmentPayDetail, id=data.get('id', None))
        if purchase_profile.completed:
            return self.payment_completed()
        # TODO:Make payment through MPESA API an return the amount paid
        # The amount (mpesa_pay_amount) should be received from MPESA API Endpoint
        mpesa_pay_amount = data.get('mpesa_pay_amount')

        # Track payment_due_date is NOT present, i.e. is FIRST TIME.
        # Add shipping & deposit then compare with the amount pay.
        if not purchase_profile.payment_due_date or purchase_profile.payment_due_date is None:
            shipping_charge = float(shipping["shipping_cost"])
            deposit = float(purchase_profile.installment_item.deposit_amount)
            if mpesa_pay_amount < (deposit + shipping_charge):
                #  If mpesa_pay_amount is LESS than deposit + shipping_charge Return response with those details
                return self.less_amount_paid(mpesa_pay_amount, deposit)
            purchase_profile.amount_paid = mpesa_pay_amount

        # If we have payment_due_date, i.e. is NOT First time
        # We have to check the dates and amount paid and remaining balance
        if purchase_profile.payment_due_date:
            previous_amount = purchase_profile.amount_paid
            # If the amount paid and the previous amount is greater than remaining_balance
            if (mpesa_pay_amount + previous_amount) > purchase_profile.remaining_balance:
                return Response({
                    'detail': f"Payment received ({mpesa_pay_amount}) is excess."
                }, status=status.HTTP_200_OK)
            purchase_profile.amount_paid = previous_amount + mpesa_pay_amount

        if (previous_amount + mpesa_pay_amount) >= (shipping + purchase_profile.installment_item.total_cost):
            purchase_profile.completed = True

        # Save the installment payment detail
        purchase_profile.save()
        serializer = s.UserInstallmentPayDetailSerializer(
            purchase_profile,
            many=False,
            context={'request': self.request}
        )
        return Response({
            'detail': "Payment Received. We will email you the details of your order. Alternatively, you can view your profile"
        }, status=status.HTTP_200_OK)

        def less_amount_paid(self, amount, deposit):
            return Response({
                'detail': f'The amount received ({amount}) is less than the REQUIRED deposit ({deposit})'
            }, status=status.HTTP_400_BAD_REQUEST)

        def payment_completed(self):
            return Response({
                'detail': "This order payment was completed."
            }, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class CreateItemReviewAPIView(APIView):
    permission_classes = [permissions.AllowAny, ]
    register_serializer_class = RegisterSerializer

    def post(self, request, format=None, *args, **kwargs):
        data = request.data
        email = data.get('email', None)
        name = data.get('name', None)
        product_id = data.get('product_id', None)
        comment = data.get('comment', None)
        save = data.get('save', None)
        ratings = data.get('ratings', None)
        if not is_valid_form([email, name, product_id, comment, save, ratings]):
            return Response({
                "detail": "Ensure the required fields are filled in."
            }, status=status.HTTP_400_BAD_REQUEST)
        item = Item.objects.get(id=product_id)
        user = _user(request)
        if user.is_authenticated:
            email = user.email
        else:
            if save == 'on':
                serializer = self.register_serializer_class({
                    'email': email,
                    'username': '',
                    'password1': name,
                    'password2': name
                }, context={"request": request})
                if serializer.is_valid():
                    serializer.save(request)
                else:
                    pass
        item_review = ItemReview.objects.create(
            email=email,
            name=name,
            item=item,
            comment=comment,
            ratings=ratings
        )
        item.rating_count.add(item_review)
        item.save()
        serializer = s.ItemReviewSerializer(item_review, many=False, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class GetUserInstallmentDetails(APIView):
    permission_classes = [permissions.AllowAny, ]
    serializer_class = s.UserInstallmentPayDetailSerializer

    def post(self, format=None, *args, **kwargs):
        user = _user(self.request)
        user_installments = UserInstallmentPayDetail.objects.filter(user=user)
        serializer = self.serializer_class(user_installments, many=True, context={"request": self.request})
        return Response(serializer.data, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class GetMessagesAPIView(APIView):
    permission_classes = [permissions.AllowAny, ]

    def get(self, format=None, *args, **kwargs):
        user = _user(self.request)
        if not user:
            user = None
        queryset = Notification.objects.for_user_or_general(user)
        serializer = s.NotificationSerializer(queryset, many=True, context={'request': self.request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, format=None, *args, **kwargs):
        user = _user(self.request)
        if not user.is_authenticated:
            return Response({"detail": "Unauthenticated user is not Allowed!"}, status=status.HTTP_200_OK)
        queryset = Notification.objects.filter(user=user)
        if queryset.exists():
            for notification in queryset:
                notification.mark_viewed()
        queryset = Notification.objects.for_user_or_general(user)
        serializer = s.NotificationSerializer(queryset, many=True, context={'request': self.request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class ShippingAddressView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny, ]
    queryset = Address.objects.all()
    serializer_class = s.AddressSerializer
    lookup_field = "pk"
