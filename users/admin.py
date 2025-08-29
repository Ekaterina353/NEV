from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class CustomUserAdmin(UserAdmin):
    # Указываем правильное поле для сортировки
    ordering = ("email",)  # Используем email вместо username
    search_fields = ("email", "first_name", "last_name")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")

    # Обновляем поля для формы редактирования
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "phone", "city", "avatar")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # Обновляем поля для формы добавления пользователя
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )

    def group_names(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])

    group_names.short_description = "Группы"
    list_display = ("email", "first_name", "last_name", "is_staff", "group_names")


# Регистрируем с кастомным админом
admin.site.register(User, CustomUserAdmin)
