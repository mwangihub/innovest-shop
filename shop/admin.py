from . import models as db
from django.contrib import admin


def mark_viewed(modeladmin, request, queryset):
    queryset.update(viewed=True)


def mark_not_viewed(modeladmin, request, queryset):
    queryset.update(viewed=False)


@admin.register(db.Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "_main", "title", "level", "viewed", "is_general", "id")
    # list_select_related = ("user", "user__profile__main_character", "user__profile__state")
    list_filter = ("level", "timestamp",)  # "user__profile__state",# ('user__profile__main_character', admin.RelatedOnlyFieldListFilter),)
    ordering = ("-timestamp",)
    actions = [mark_viewed, mark_not_viewed, ]

    # actions = [mark_viewed]
    # search_fields = ["user__username", "user__profile__main_character__character_name"]

    def _main(self, obj):
        try:
            return obj.user.profile.main_character
        except AttributeError:
            return obj

    _main.admin_order_field = "user__profile__main_character__character_name"

    def _state(self, obj):
        try:
            return obj.user.profile.state
        except:
            return obj.user

    _state.admin_order_field = "user__profile__state__name"

    # def has_change_permission(self, request, obj=None) -> bool:
    #     return False

    # def has_add_permission(self, request) -> bool:
    #     return False


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
    list_display = ['item', "area_code", "shipping_cost"]
    list_filter = ['item', ]


admin.site.register(db.GenericForeignKeyModel, GenericForeignKeyModelAdmin)
admin.site.register(db.ItemInstallmentDetail, ItemInstallmentDetailsAdmin)
admin.site.register(db.UserInstallmentPayDetail, UserInstallmentPayDetailAdmin)
admin.site.register(db.ShippingLocationCharges)
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
admin.site.register(db.Payment)
admin.site.register(db.Coupon)
admin.site.register(db.Refund)
admin.site.register(db.ItemSample)
