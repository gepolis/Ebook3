from django.contrib import admin
from .models import *


@admin.register(Events)
class EventsAdminModel(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date")


@admin.register(Subjects)
class SubjectsModelAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(EventCategory)
class SubjectsModelAdmin(admin.ModelAdmin):
    list_display = ("name",)
