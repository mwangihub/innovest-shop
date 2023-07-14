from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Notification

User = get_user_model()


def add_all_users(modeladmin, request, queryset):
    all_users = User.objects.all()
    for notification in queryset:
        notification.users.add(*all_users)
        notification.user = None
        notification.for_user = False
        notification.save()


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "for_user","timestamp", "unread_users", "read_users", "level", "id")
    # list_select_related = ("user", "user__profile__main_character", "user__profile__state")
    list_filter = ("level", "timestamp",)  # "user__profile__state",# ('user__profile__main_character', admin.RelatedOnlyFieldListFilter),)
    ordering = ("-timestamp",)
    actions = [add_all_users, ]

    # search_fields = ["user__username", "user__profile__main_character__character_name"]

    def unread_users(self, obj):
        if obj.for_user:
            return "for user"
        return obj.users.count()

    # _main.admin_order_field = "user__profile__main_character__character_name"

    def read_users(self, obj):
        if obj.for_user:
            return "for user"
        users = User.objects.all().count()
        read_by = users - self.unread_users(obj)
        return read_by

    # def has_change_permission(self, request, obj=None) -> bool:
    #     return False

    # def has_add_permission(self, request) -> bool:
    #     return False
