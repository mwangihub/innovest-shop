from . import models as db
from django.contrib import admin




# Register your models here.
class ItemImages(admin.StackedInline):
    model = db.ItemPicture


# class ItemColorChoiceAdmin(admin.ModelAdmin):
#     model = db.ItemColorChoice


class ItemAdmin(admin.ModelAdmin):
    inlines = (ItemImages,)
    list_filter = ('category', 'title')
    list_display = ('title', 'category', 'stock', "discounted_price", "price")


class OrderAdmin(admin.ModelAdmin):
    list_filter = ('ordered', 'received', "refund_requested", "refund_granted")
    list_display = ("ref_code", 'ordered', 'being_delivered', "refund_requested", "refund_granted", 'received',)


class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "first_name", "last_name", "address", "state", "country", "phone", "_default", "id")


class GenericForeignKeyModelAdmin(admin.ModelAdmin):
    list_display = ("db_type", "content_type")


class ItemInstallmentDetailsAdmin(admin.ModelAdmin):
    list_display = ("item", "total_cost", "deposit_amount", "payment_period")


class UserInstallmentPayDetailAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "selected_address",
        "payment_period",
        "payment_period_start_date",
        "amount_paid",
        "next_amount_to_pay",
        "remaining_balance",
        "payment_due_date",
        "paid_for_period",
        "selected_shipping_charges",
        "required_period",
        "completed",
        "mpesa_no",
        "id"
    )

    def payment_period(self, instance):
        return instance.installment_item.payment_period


class ShippingChargeAdmin(admin.ModelAdmin):
    list_display = ["town", "shipping_cost", 'item', ]
    list_filter = ['town', ]

class PaymentAdmin(admin.ModelAdmin):
        list_display = ['id', ]


admin.site.register(db.GenericForeignKeyModel, GenericForeignKeyModelAdmin)
admin.site.register(db.ItemInstallmentDetail, ItemInstallmentDetailsAdmin)
admin.site.register(db.UserInstallmentPayDetail, UserInstallmentPayDetailAdmin)
# admin.site.register(db.ShippingLocationCharges)
admin.site.register(db.Town)
admin.site.register(db.ItemBrandName)
admin.site.register(db.ShippingCharge, ShippingChargeAdmin)
admin.site.register(db.ItemColor)
admin.site.register(db.ItemBrand)
admin.site.register(db.ItemSizeByMode)
admin.site.register(db.ItemManufacturer)
admin.site.register(db.ItemSizeByNumber)
admin.site.register(db.ItemSubCategory)
admin.site.register(db.ItemCategory)
admin.site.register(db.ItemTrending)
admin.site.register(db.ItemColorChoice)
admin.site.register(db.ItemPicture)
admin.site.register(db.Item, ItemAdmin)
admin.site.register(db.ItemReview)
admin.site.register(db.RELATED_DB_TYPES_FOR_ITEMS)

admin.site.register(db.CartItem)
admin.site.register(db.Order, OrderAdmin)
admin.site.register(db.CustomerPurchaseProfile)
admin.site.register(db.Address, AddressAdmin)
admin.site.register(db.Payment, PaymentAdmin)
admin.site.register(db.Coupon)
admin.site.register(db.Refund)
