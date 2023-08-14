from django.contrib import admin
from .models import *


@admin.register(Account)
class SnippetModelAdmin(admin.ModelAdmin):
    list_display = ("pk", "username", "second_name", "first_name", "middle_name", "email", "is_staff", "is_superuser")
    list_filter = ("is_superuser",)
    readonly_fields = ("password",)
    fieldsets = (
        ('', {
            'fields': (
            'username', 'email', ('second_name', 'first_name', 'middle_name'), "building","peculiarity")
        }),
        ('Permissions', {
            'fields': ("is_staff", "is_superuser","role")
        }),
    )


@admin.register(Building)
class SnippetModelAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "type")


