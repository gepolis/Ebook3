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

from django.apps import apps

for model in apps.get_models():
    model_admin = type(f"{model.__name__}Admin", (admin.ModelAdmin,), {})

    model_admin.list_display = model.admin_list_display if hasattr(model, 'admin_list_display') else tuple([field.name for field in model._meta.fields])
    model_admin.list_filter = model.admin_list_filter if hasattr(model, 'admin_list_filter') else model_admin.list_display
    model_admin.ordering = model.admin_ordering if hasattr(model, 'admin_ordering') else ()
    model_admin.list_display_links = model.admin_list_display_links if hasattr(model, 'admin_list_display_links') else ()
    model_admin.list_editable = model.admin_list_editable if hasattr(model, 'admin_list_editable') else ()
    model_admin.search_fields = model.admin_search_fields if hasattr(model, 'admin_search_fields') else ()
    try:
        admin.site.register(model, model_admin)
    except admin.sites.AlreadyRegistered:
        pass