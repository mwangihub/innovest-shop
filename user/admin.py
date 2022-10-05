from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from user.forms import UserAdminCreationForm, UserAdminChangeForm
from . import models as acc_db


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    search_fields = ["email", "first_name", "last_name"]
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    # The fields to be used in displaying the CustomUser model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.CustomUser.'admin', 'active', 'staff', "first_name", "last_name",'id',
    list_display = ("email", "username", 'id', "first_name", "last_name", "is_admin",
                    "is_active", "is_staff", "buyer", "employee", "non",)
    list_filter = ("is_admin", "is_active", "is_staff")
    fieldsets = (
        ("Basic", {"fields": ("email", "username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name",)}),
        ("Permissions", {"fields": ("is_admin", "is_active", "is_staff",)},),
        ("Authorization", {"fields": ("buyer", "employee", "non")},),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "username", "password2", "first_name",
                                                 "last_name", "is_active", "is_staff", "is_admin", "buyer", "employee",
                                                 "non"), },),
    )
    ordering = ("email",)
    filter_horizontal = ()


class BuyerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', "phone", "address", "created_at", "updated_at"]


class InnovestUsersMessagesAdmin(admin.ModelAdmin):
    list_display = ("names", "email", "subject", "created_at", "session_user")


class DebugFrontEndAdmin(admin.ModelAdmin):
    list_display = ("project", "debug",)


admin.site.unregister(Group)
admin.site.register(acc_db.User, UserAdmin)
admin.site.register(acc_db.DebugFrontEnd, DebugFrontEndAdmin)
admin.site.register(acc_db.Project)
admin.site.register(acc_db.BuyerProfile, BuyerProfileAdmin)
admin.site.register(acc_db.InnovestUsersMessages, InnovestUsersMessagesAdmin)

admin.site.site_title = "Innovest Shop Admin panel"
admin.site.index_title = "Innovest Shop | Developer/Admin panel "
admin.site.site_header = "Innovest Shop | Developer/Admin panel Dashboard"

admin.site.site_title = "Innovest Shop Administrator panel"
admin.site.index_title = "Innovest Shop | Administrator panel "
admin.site.site_header = "Innovest Shop | Administrator panel Dashboard"
