from django.contrib import admin
from MainApp.models import Events


@admin.register(Events)
class EventsAdminModel(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date")
    filter_horizontal = ("classroom_number",)
