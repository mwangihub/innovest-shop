from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView, UpdateAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from core.methods import _user
from shop.models import *
from . import serializers

channel_layer = get_channel_layer()
User = get_user_model()


@method_decorator(csrf_exempt, name="dispatch")
class UpdateUserInstallmentAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None, *args, **kwargs):
        return Response({}, status=status.HTTP_200_OK)


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
        pk = request.data.get("profile_id", None)
        installment_pay_detail = get_object_or_404(UserInstallmentPayDetail, pk=pk)
        if request.data.get("amount_paid", None) is None:
            if request.data.get("address", None):
                address = get_object_or_404(Address, pk=request.data.get("id"))
                data = {"selected_address": address}

            if request.data.get("selected_shipping_charges", None):
                selected_shipping_charges = get_object_or_404(ShippingCharge, pk=request.data.get("id"))
                data = {"selected_shipping_charges": selected_shipping_charges}

            if request.data.get("mpesa", None):
                mpesa_no = request.data.get("mpesa_no", None)
                data = {"mpesa_no": mpesa_no}
        else:
            data = {"amount_paid": request.data.get("amount_paid", None)}
            if request.data.get("mpesa_no", None):
                data["mpesa_no"] = request.data.get("mpesa_no", None)
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
