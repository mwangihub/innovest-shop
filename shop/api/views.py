# Create your views here.
import random
import string

import requests
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from rest_framework import status, permissions, generics
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.models import *
from . import serializers as s
from core.methods import _user


def create_ref_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))


User = get_user_model()


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


class TrendingItemsListAPIView(ListAPIView):
    serializer_class = s.ItemTrendingSerializer
    permission_classes = [permissions.AllowAny, ]

    def get_queryset(self):
        queryset = ItemTrending.objects.all()[:3]
        return queryset


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


class AddressAPIView(generics.ListAPIView):
    permissions_classes = [permissions.AllowAny, ]
    queryset = Address.objects.all()
    serializer_class = s.AddressSerializer


class ItemsAPIView(APIView):
    """
    The get function returns a list of all items in the database.
    :param self: Reference the class itself
    :param request: Access the request made by the client
    :param format=None: Specify the format of the data being returned
    :return: A list of all the items in the database
    :doc-author: Trelent
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        queryset = Item.objects.all()
        serializer = s.ItemSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# REQUIRE AUTHENTICATION
# @method_decorator(csrf_protect, name="dispatch")
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
        user = _user(request)
        if slug is None:
            return Response({"details": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        item = get_object_or_404(Item, slug=slug)
        item.stock -= quantity
        item.save()
        order_item, created = CartItem.objects.get_or_create(item=item, user=user, ordered=False)
        order_qs = Order.objects.filter(user=user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if order.items.filter(item__slug=item.slug).exists():
                order_item.quantity += 1
                order_item.save()
            else:
                order_item.quantity = quantity
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
            order_item.quantity = quantity
            order_item.save()
            order.items.add(order_item)
            return Response({
                "details": f"{item.title} added to your cart",
                "item": self.item_serializer(item, context={"request": request}).data,
                "order": self.order_serializer(order, context={"request": request}).data,
                "items": s.ItemSerializer(Item.objects.all(), many=True, context={"request": request}).data,
            }, status=status.HTTP_200_OK)


@method_decorator(csrf_protect, name="dispatch")
class DeleteItemFromCartView(APIView):
    """
    - Api that provide functionality to delete item from the cart
    - User must be authenticated
    """
    permission_classes = [permissions.IsAuthenticated, ]

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


@method_decorator(csrf_protect, name="dispatch")
class ReduceItemQuantityView(APIView):
    """
    - Api that provide functionality to reduce item from the cart by 1
    - User must be authenticated
    """
    permission_classes = [permissions.IsAuthenticated, ]

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


@method_decorator(csrf_protect, name="dispatch")
class AddItemQuantityAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

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
            return Response(self.serializer_class(order, many=False, context={'request': self.request}).data, status=status.HTTP_200_OK)
        return Response({"order": None}, status=status.HTTP_200_OK)


class CompletedOrderView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = s.OrderSerializer

    def get_queryset(self):
        user = _user(self.request)
        order = Order.objects.all()
        return order


@method_decorator(csrf_protect, name="dispatch")
class AddCouponView(APIView):
    """
    - Api that adds a coupon to the  order and reduces the amount charged with the value of the coupon
    - User must be authenticated
    """
    permission_classes = [permissions.IsAuthenticated, ]

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
            print(serializer.errors)
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


@method_decorator(csrf_protect, name="dispatch")
class CrudShippingAddrView(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

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
            serializer = s.AddressSerializer(instance=address, data=data, many=False, partial=True, context={'request': self.request})
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
            serializer = s.AddressSerializer(initial={'country': 'KE'}, data=data, many=False, context={'request': self.request})
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


class MpesaPay(APIView):
    permission_classes = [permissions.AllowAny, ]

    def post(self, request, format=None, *args, **kwargs):
        pay_id = request.data.get("pay_id")
        amount = request.data.get("amount")

        user = _user(request)
        try:
            order = Order.objects.get(user=user, ordered=False)
        except Order.DoesNotExist:
            return Response({
                "order": None,
                'details': "Order payment was done"
            }, status=status.HTTP_400_BAD_REQUEST)
        total = order.get_total
        if amount != total:
            return Response({
                "order": s.OrderSerializer(order, context={"request": request}).data,
                'details': "Amount discrepancy. Payment failed"
            }, status=status.HTTP_400_BAD_REQUEST)
        payment = Payment.objects.create(
            user=user,
            stripe_charge_id=pay_id,
            amount=amount
        )
        order.payment = payment
        order_items = order.items.all()
        order_items.update(ordered=True)
        for item in order_items:
            qty = item.quantity
            if item.item.stock >= qty:
                item.item.stock -= qty
            item.item.save()
            item.save()
        order.ordered = True
        order.save()
        return Response({
            "order": s.OrderSerializer(order, context={"request": request}).data,
            'details': "Successfully transacted through Mpesa"
        }, status=status.HTTP_200_OK)
