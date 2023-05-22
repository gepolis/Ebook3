from django.contrib import admin
from .models import *
@admin.register(Notications)
class SnippetModelAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "created", "viewed")
