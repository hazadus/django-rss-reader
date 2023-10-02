from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Configures admin panel views for CustomUsers.
    """

    model = CustomUser
    list_display = [
        "username",
        "is_staff",
    ]
    # Which fields to show when editing user via admin panel:
    fieldsets = UserAdmin.fieldsets + (
        (
            None,
            {"fields": ("profile_image",)},
        ),
    )
    # Which fields to show when creating user via admin panel:
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            None,
            {"fields": ("profile_image",)},
        ),
    )
