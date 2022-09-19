from django.contrib import admin
from . import models as db


# Register your models here.

class ItemAdmin(admin.ModelAdmin):
    list_filter = ('category', 'title')
    list_display = ('title', 'category',)


class OrderAdmin(admin.ModelAdmin):
    list_filter = ('ordered', 'received', "refund_requested", "refund_granted")
    list_display = ("ref_code", 'ordered', 'being_delivered', "refund_requested", "refund_granted", 'received',)


class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "first_name", "last_name", "address", "state", "country", "phone", "_default")


admin.site.register(db.Item, ItemAdmin)
admin.site.register(db.ItemReview)
admin.site.register(db.CartItem)
admin.site.register(db.Order, OrderAdmin)
admin.site.register(db.CustomerPurchaseProfile)
admin.site.register(db.Address, AddressAdmin)
admin.site.register(db.Payment)
admin.site.register(db.Coupon)
admin.site.register(db.Refund)
admin.site.register(db.ItemSample)
