from django.urls import path, include
from . import views
from .views_functions import *  # NOQA

views_patterns = [
    path('user-installment-detail/', include([
        path("create/", UserInstallmentPayDetailCreateAPIView.as_view(), name="installment_detail_create"),
        path("patch/", UserInstallmentPayDetailCreateAPIView.as_view(), name="installment_detail_patch"),
    ])),
    path("billings/", PaymentAPIView.as_view(), name="billings"),
    path("billings-detail/", PaymentAPIView.as_view(), name="billings_detail"),
]
main_patterns = [
    path("auto-items/", views.AutoCreateProducts.as_view(), name="auto-items"),
    path("items-detail/<slug>/", views.ItemDetailView.as_view(), name="item-detail"),
    path("items-list/", views.ItemsAPIView.as_view(), name="item-list"),
    path("order-summary/", views.OrderDetailView.as_view(), name="order-summary", ),
    path("order-detail/", views.OrderDetailView.as_view(), name="order-detail", ),
    path("completed-order/", views.CompletedOrderView.as_view(), name="completed-order", ),
    path("add-coupon/", views.AddCouponView.as_view(), name="add-coupon", ),
    path("addresses/", views.AddressAPIView.as_view(), name="addresses", ),
    path("retrieve-address/", views.RetrieveAddress.as_view(), name="get-address", ),
    path("create-addresses/", views.CreateAddressView.as_view(), name="create-addresses", ),
    path("mpesa-pay/", views.MpesaPay.as_view(), name="mpesa-pay", ),
    path("crud-shippingAddr/", views.CrudShippingAddrView.as_view(), name="crud_shippingAddr"),
    path("shipping-addrs/<int:pk>/", views.ShippingAddressView.as_view(), name="crud_shippingAddr"),

    path("delete-from-cart/<str:slug>/", views.DeleteItemFromCartView.as_view(), name="delete-from-cart", ),
    path("delete-from-cart/", views.DeleteItemFromCartView.as_view(), name="delete-from-cart", ),

    path("reduce-from-cart/<str:slug>/", views.ReduceItemQuantityView.as_view(), name="reduce-from-cart", ),
    path("reduce-from-cart/", views.ReduceItemQuantityView.as_view(), name="reduce-from-cart", ),

    path("add-items-to-cart/<str:slug>/", views.AddItemQuantityAPIView.as_view(), name="add-items-to-cart", ),
    path("add-items-to-cart/", views.AddItemQuantityAPIView.as_view(), name="add-items-to-cart", ),

    path("add-to-cart/<str:slug>/", views.AddToCartAPIView.as_view(), name="add-to-cart", ),
    path("add-to-cart/", views.AddToCartAPIView.as_view(), name="add-to-cart", ),

    path("trending-items/", views.TrendingItemsListAPIView.as_view(), name="trending_items", ),
    path("items-category/", views.ItemsCategoriesListAPIView.as_view(), name="items_category", ),
    path("get-user-installmentDetails/", views.GetUserInstallmentDetails.as_view(), name="get_user_installmentDetails", ),

    path("purchase-with-installment/", views.PurchaseWithInstallMentAPIView.as_view(), name="purchase_with_installment", ),
    path("purchase-installment-profile/", views.PurchaseInstallMentProfileAPIView.as_view(), name="purchase_installment_profile", ),
    path("complete-installment-payment/", views.CompleteInstallmentPayAPIView.as_view(), name="complete_installment_payment", ),
    path("create-item-review/", views.CreateItemReviewAPIView.as_view(), name="create-item-review", ),
]

urlpatterns = main_patterns + views_patterns
