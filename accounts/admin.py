from django.contrib import admin

# Register your models here.



from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "full_name", "subscription_plan", "business_stage", "is_active")
    list_filter = ("subscription_plan", "business_stage", "is_active")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("full_name", "profile_picture")}),
        ("Business Context", {"fields": ("business_stage", "industry", "target_market", "budget_range", "skills_background")}),
        ("Subscription & Usage", {"fields": ("subscription_plan", "api_tokens_used", "ideas_created", "messages_sent")}),
        ("Security", {"fields": ("two_factor_enabled", "is_verified", "is_active", "is_staff", "is_superuser")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "password1", "password2", "subscription_plan", "is_active"),
        }),
    )

    search_fields = ("email", "full_name")
    ordering = ("email",)
