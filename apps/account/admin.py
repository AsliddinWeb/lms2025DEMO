from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, StudentProfile, TeacherProfile


# Custom User admin
class UserAdmin(BaseUserAdmin):
    # admin panelda ko'rinadigan ustunlar
    list_display = ("username", "role", "is_staff", "is_active", "date_joined")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "first_name", "last_name")
    ordering = ("username",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (_("Permissions"), {"fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "password1", "password2", "role", "is_active", "is_staff", "is_superuser"),
        }),
    )


# Student Profile admin
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "first_name", "last_name", "father_name", "phone")
    search_fields = ("first_name", "last_name", "father_name", "user__username")
    list_filter = ("birth_date",)


# Teacher Profile admin
@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "first_name", "last_name", "father_name", "phone")
    search_fields = ("first_name", "last_name", "father_name", "user__username")
    list_filter = ("birth_date",)


# CustomUser registratsiya
admin.site.register(User, UserAdmin)
