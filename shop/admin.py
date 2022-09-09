from django.contrib import admin
from . import models as db


# Register your models here.

class ItemAdmin(admin.ModelAdmin):
    list_filter = ('category', 'title')
    list_display = ('title', 'category',)


admin.site.register(db.Item, ItemAdmin)
admin.site.register(db.ItemReview)
admin.site.register(db.CartItem)
admin.site.register(db.Order)
admin.site.register(db.CustomerPurchaseProfile)
admin.site.register(db.Address)
admin.site.register(db.Payment)
admin.site.register(db.Coupon)
admin.site.register(db.Refund)
admin.site.register(db.ItemSample)
