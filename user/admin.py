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
    list_display = ("email", 'id', "first_name", "last_name", "is_admin",
                    "is_active", "is_staff", "buyer", "employee", "non",)
    list_filter = ("is_admin", "is_active", "is_staff")
    fieldsets = (
        ("Basic", {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name",)}),
        ("Permissions", {"fields": ("is_admin", "is_active", "is_staff",)},),
        ("Authorization", {"fields": ("buyer", "employee", "non")},),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2", "first_name",
                                                 "last_name", "is_active", "is_staff", "is_admin", "buyer", "employee",
                                                 "non"), },),
    )
    ordering = ("email",)
    filter_horizontal = ()



admin.site.site_title = "Innovest Shop Developer/Admin pannel"
admin.site.index_title = "Innovest Shop | Developer/Admin pannel "
admin.site.site_header = "Innovest Shop | Developer/Admin pannel Dashboard"

admin.site.site_title = "Django Shop Administrator pannel"
admin.site.index_title = "Django Shop | Administrator pannel "
admin.site.site_header = "Django Shop | Administrator pannel Dashboard"

admin.site.unregister(Group)
admin.site.register(acc_db.User, UserAdmin)
