from django.urls import path
from . import views

urlpatterns = [
    path("auto-items/", views.AutoCreateProducts.as_view(), name="auto-items"),
    path("items-detail/<slug>/", views.ItemDetailView.as_view(), name="item-detail"),
    path("items-list/", views.ItemsAPIView.as_view(), name="item-list"),
    # path("cart-items/", views.CartItemsAPIView.as_view(), name="cart-items"),
    path("delete-from-cart/", views.DeleteItemFromCartView.as_view(), name="delete-from-cart", ),
    path("reduce-from-cart/", views.ReduceItemFromCartView.as_view(), name="reduce-from-cart", ),
    path("add-items-to-cart/", views.AddItemToCartView.as_view(), name="add-items-to-cart", ),
    path(  # "add-to-cart/<str:slug>/",v.AddToCartAPIView.as_view(),name="add-to-cart",
        "add-to-cart/", views.AddToCartAPIView.as_view(), name="add-to-cart", ),
    path("order-summary/", views.OrderDetailView.as_view(), name="order-summary", ),
    path("completed-order/", views.CompletedOrderView.as_view(), name="completed-order", ),
    path("add-coupon/", views.AddCouponView.as_view(), name="add-coupon", ),
    path("addresses/", views.AddressAPIView.as_view(), name="addresses", ),
    path("retrieve-address/", views.RetrieveAddress.as_view(), name="get-address", ),
    path("create-addresses/", views.CreateAddressView.as_view(), name="create-addresses", ),
    path("mpesa-pay/", views.MpesaPay.as_view(), name="mpesa-pay", ),
]
