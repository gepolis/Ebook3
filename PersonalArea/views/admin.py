import uuid
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from Accounts.models import Account
from MainApp.models import *
from django.utils.formats import localize

from PersonalArea.forms import *
from Accounts.forms import NewBuildingForm
from Accounts.models import Building
from Accounts import decorators
import io
import xlsxwriter
import pandas as pd
from PersonalArea.models import Notications, Message


@decorators.is_admin
def view_user(request, id):
    user = Account.objects.get(pk=id)
    if not user.is_superuser:
        return render(request, "adminpanel/view_user.html", {"view_user": user})
    return redirect("/lk/users/list")

@decorators.is_admin
def login_admin_user(request, user):
    if request.user.is_superuser:
        logout(request)
        user = get_object_or_404(Account, pk=user)
        login(request, user)
        return redirect("/lk/")
@decorators.is_admin
def users_list(request, role=None):
    users = Account.objects.all().filter(is_superuser=False).order_by("-id")

    create_user_form = NewUserForm()
    context = {
        "count_users": users.count(),
        "count_staff": users.filter(role__in=["teacher", "methodist"]).count(),
        "count_parents": users.filter(role="parent").count(),
        "count_students": users.filter(role="student").count(),
        "create_user_form": create_user_form,
        "section": "users"
    }
    if request.GET.get("role"):
        users = users.filter(role=request.GET.get("role"))
    paginator = Paginator(users, settings.ITEMS_FOR_PAGE)  # Show 25 contacts per page.
    page_number = request.GET.get("page")
    if page_number is None:
        page_number = 1
    page_obj = paginator.get_page(page_number)
    context["users"] = page_obj
    context["role"] = request.GET.get("role")
    return render(request, "adminpanel/users_list.html", context=context)


@decorators.is_admin
def user_create(request):
    if request.method == "GET":
        return redirect("/lk/users/list")
    else:
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=True)
        return redirect("/lk/users/list")
    return render(request, "adminpanel/user_create.html", {"form": form})


@decorators.is_admin
def edit_user(request, id):
    user = Account.objects.get(pk=id)
    if request.method == "GET":
        form = EditUserForm(instance=user)
    else:
        form = EditUserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
        return redirect("/lk/users/list")
    return render(request, "adminpanel/edit_user.html", {"form": form, "section": "users", "table_user": user})


@decorators.is_admin
def avatar_remove(request, user):
    user = get_object_or_404(Account, pk=user)
    user.avatar = None
    user.save()
    return redirect(f"/lk/users/{user.pk}/edit")


@decorators.is_admin
def event_add_user(request, id, user):
    user = Account.objects.get(id=user)
    user = EventsMembers(user=user, is_active=False)
    user.save()
    event = Events.objects.get(pk=id)
    event.volunteer.add(user)
    return redirect(f"/lk/events/{id}/view")


@decorators.is_admin
def add_building(request):
    if request.method == "GET":
        form = NewBuildingForm()
    else:
        form = NewBuildingForm(request.POST)
        if form.is_valid():
            user = form.save(commit=True)
        return redirect("/lk/building/list")
    return render(request, "adminpanel/building_create.html", {"form": form, "section": "building"})


@decorators.is_admin
def building_list(request):
    context = {
        "buildings": Building.objects.all().order_by("-id"),
        "section": "building"
    }
    return render(request, "adminpanel/buildings_list.html", context=context)


@decorators.is_admin
def user_data(request, id):
    user = Account.objects.get(pk=id)
    user_data = {
        'received': localize(datetime.now()),
        'user': {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name(),
            "email": user.email,
            "date_joined": localize(user.date_joined),
            "last_login": localize(user.last_login),
            "role": {
                "display": user.get_role_display(),
                "role": user.role
            },
        },
        "events": {}
    }
    for i in EventsMembers.objects.all().filter(user=user):
        event = Events.objects.get(volunteer=i)
        user_data['events'][i.pk] = {
            "event": {
                "id": event.pk,
                "name": event.name,
                "description": event.description,
                "start": event.start_date,
                "end": event.end_date
            },
            "points": i.points

        }
    return JsonResponse(user_data, safe=False)


@decorators.is_admin
def category_list(request):
    if request.method == "POST":
        form = EventCategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
    categories = EventCategory.objects.all()
    form = EventCategoryForm()
    return render(request, "adminpanel/category_list.html", {"categories": categories, "form": form, "section": "events"})


@decorators.is_admin
def category_data(request, id):
    category = EventCategory.objects.get(pk=id)
    category_data = {
        'received': localize(datetime.now()),
        'category': {
            "id": category.id,
            "name": category.name,
            "methodists": {}
        }
    }
    for i in category.methodists.all():
        category_data['category']['methodists'][i.pk] = {
            "id": i.pk,
            "full_name": i.full_name(),

        }
    return JsonResponse(category_data, safe=False)


@decorators.is_admin
def category_edit(request, id):
    category = EventCategory.objects.get(pk=id)
    if request.method == "POST":
        form = EventCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            form.save_m2m()
        return redirect("category_list")
    else:
        form = EventCategoryForm(instance=category)
        return render(request, "adminpanel/edit_category.html", {"section": "events", "form": form})


@decorators.is_admin
def classrooms_list(request):
    classrooms = ClassRoom.objects.all()
    return render(request, "adminpanel/classrooms.html", {"classrooms": classrooms, "section": "classrooms"})


@decorators.is_admin
def classrooms_view(request, id):
    classrooms = get_object_or_404(ClassRoom, id=id)
    msgs = Message.objects.all().filter(room=classrooms.id)[0:25]
    return render(request, "adminpanel/classroom_view.html", {"classroom": classrooms, "msgs": msgs, "section": "classrooms"})
