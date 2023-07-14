from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView, UpdateAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from core.methods import _user, create_unique_code
from shop.models import *
from . import serializers
from .serializers import PaymentSerializer

channel_layer = get_channel_layer()
User = get_user_model()


@method_decorator(csrf_exempt, name="dispatch")
class PaymentAPIView(APIView):
    permission_classes = [permissions.AllowAny, ]
    serializer_class = PaymentSerializer

    def get(self, format=None, *args, **kwargs):
        user = _user(self.request)
        # billing_id = self.request.data.get('billing_id', None)
        queryset = Payment.objects.filter(user=user)
        serializer = PaymentSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        user = _user(self.request)
        billing_id = self.request.data.get('billing_id', None)
        try:
            queryset = Payment.objects.get(user=user, stripe_charge_id=billing_id)
        except Payment.DoesNotExist:
            return Response({
                "detail": 'Billing detail does not exist.'
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = PaymentSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserInstallmentPayDetailCreateAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.UserInstallmentPayDetailSerializer

    def post(self, request, format=None):
        installment_item_id = (request.data.get("installment_item", None))
        installment_item = get_object_or_404(ItemInstallmentDetail, pk=installment_item_id)
        data = {
            "installment_item": installment_item,
            "required_period": request.data.get("payment_period", None)
        }
        serializer = self.serializer_class(data=data, context={"request": request})
        if serializer.is_valid():
            # installment_item  is not passed in validated data since in serializer is passed as a read_only field
            # installment_item = serializer.validated_data['installment_item']
            required_period = serializer.validated_data['required_period']
            serializer.save(
                required_period=required_period,
                installment_item=installment_item,
                # To Ensure that the instance is unique from others with paid_amount otherwise
                # it would replace the instance
                amount_paid=0
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, format=None):
        data = None
        user = _user(request)
        pk = request.data.get("profile_id", None)
        try:
            installment_pay_detail = UserInstallmentPayDetail.objects.get(id=pk)
        except UserInstallmentPayDetail.DoesNotExist:
            return Response({"detail": "User payment details not found"}, status=status.HTTP_404_NOT_FOUND)

        if request.data.get("amount_paid", None) is None:
            # No Payment is made
            if request.data.get("address", None) and not request.data.get("create_address", None):
                address = get_object_or_404(Address, pk=request.data.get("id"))
                data = {"selected_address": address}

            if request.data.get("selected_shipping_charges", None):
                selected_shipping_charges = get_object_or_404(ShippingCharge, pk=request.data.get("id"))
                data = {"selected_shipping_charges": selected_shipping_charges}

            if request.data.get("mpesa", None):
                mpesa_no = request.data.get("mpesa_no", None)
                data = {"mpesa_no": mpesa_no}

            if request.data.get("create_address", None) and request.data.get("address", None):
                serializer = serializers.AddressSerializer(data=request.data, context={"request": request})
                if serializer.is_valid():
                    address = serializer.save()
                    print(address)
                    data = {"selected_address": address}

        else:
            # User has made payment
            amount_paid = request.data.get("amount_paid", None)
            mpesa_no = request.data.get("mpesa_no", None)
            pay_id = request.data.get("pay_id", None)
            describe = request.data.get("describe", None)
            color = request.data.get("color", None)
            size = request.data.get("size", None)
            payment = Payment.objects.create(
                user=user,
                stripe_charge_id=pay_id,
                amount=amount_paid,
                mpesa_no=mpesa_no,
                shipping=f'For installment ({installment_pay_detail.selected_shipping_charges.town.name}) - {installment_pay_detail.selected_shipping_charges.shipping_cost}',
                installment_item=f'Installment item: {installment_pay_detail.installment_item.item.title}, Period: {installment_pay_detail.installment_item.payment_period} Months'
            )
            data = {
                "amount_paid": amount_paid,
                "mpesa_no": mpesa_no,
                "color": color,
                "describe": describe,
                "size": size,
                "payment": payment,
            }
            # if mpesa_no:
            #     data["mpesa_no"] = mpesa_no
        serializer = self.serializer_class(instance=installment_pay_detail, data=data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save(**data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserInstallmentPayDetailUpdateAPIView(UpdateAPIView):
    serializer_class = serializers.UserInstallmentPayDetailSerializer
    queryset = UserInstallmentPayDetail.objects.all()

    def perform_update(self, serializer):
        # This view should get installment_item from  UserInstallmentPayDetail
        amount_paid = serializer.validated_data['amount_paid']
        # Remaining balance should be calculated
        remaining_balance = serializer.validated_data['remaining_balance']
        installment_item = serializer.instance.installment_item
        required_period = serializer.instance.required_period
        paid_for_period = serializer.instance.paid_for_period
        payment_due_date = serializer.instance.payment_due_date
        next_amount_to_pay = max(
            remaining_balance,
            installment_item.deposit_amount
        ) / (required_period - paid_for_period + 1)

        paid_for_period += 1
        payment_due_date += timedelta(days=30)
        serializer.save(
            next_amount_to_pay=next_amount_to_pay,
            paid_for_period=paid_for_period,
            payment_due_date=payment_due_date
        )
