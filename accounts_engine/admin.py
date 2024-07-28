from django.contrib import admin
from .models import CustomUser, InvalidatedToken
from django.contrib.auth.admin import UserAdmin


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "contact", "is_active", "is_admin", "created_datetime", "updated_datetime", "is_delete")
    search_fields = ("username", "contact")
    list_filter = ("is_active", "is_admin", "is_delete")
    ordering = ("-created_datetime",)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("contact", "about")}),
        ("Permissions", {"fields": ("is_active", "is_admin")}),
        ("Important dates", {"fields": ("last_login", "created_datetime", "updated_datetime")}),
        ("Status", {"fields": ("is_delete", "deleted_contact_number", "otp", "otp_send_datetime", "last_otp_status")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("contact", "password1", "password2"),
            },
        ),
    )


@admin.register(InvalidatedToken)
class InvalidatedTokenAdmin(admin.ModelAdmin):
    list_display = ("token", "invalidated_at")
    search_fields = ("token",)
    list_filter = ("invalidated_at",)
    ordering = ("-invalidated_at",)
