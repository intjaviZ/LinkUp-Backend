from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("email",)
    list_display = ("email", "nombre", "plan_estudiantil", "cuatrimestre_actual", "is_staff")
    list_filter = ("plan_estudiantil", "is_staff", "is_active")
    search_fields = ("email", "nombre")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Perfil", {"fields": ("nombre", "plan_estudiantil", "cuatrimestre_actual", "biografia")}),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Fechas", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "nombre", "plan_estudiantil", "cuatrimestre_actual", "password1", "password2"),
        }),
    )