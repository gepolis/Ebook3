from django.conf import settings

from django.contrib.auth import logout, login

from django.core.paginator import Paginator
from django.http import JsonResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404

from MainApp.models import *
from django.utils.formats import localize

from PersonalArea.forms import *

from Accounts import decorators

from PersonalArea.models import Notications, Message


@decorators.is_school_administrator
def view_user(request, id):
    user = Account.objects.get(pk=id)
    if request.user.role == "head_teacher":
        if request.user.building != user.building:
            return redirect("/lk/users/list")
    if not user.is_superuser:
        return render(request, "administration/view_user.html", {"view_user": user})

    return redirect("/lk/users/list")




@decorators.is_school_administrator
def users_list(request, role=None):
    users = Account.objects.all().filter(is_superuser=False).order_by("-id")
    if request.user.role == "head_teacher":
        users = users.filter(building=request.user.building)

    create_user_form = NewUserForm()
    context = {
        "count_users": users.count(),
        "count_staff": users.filter(role__in=["teacher", "methodist"]).count(),
        "count_parents": users.filter(role="parent").count(),
        "count_students": users.filter(role="student").count(),
        "create_user_form": create_user_form,
        "section": "users",
        "can_create": False
    }
    if request.user.role == "admin" or request.user.role == "director":
        context["can_create"] = True
    if request.GET.get("role"):
        users = users.filter(role=request.GET.get("role"))
    paginator = Paginator(users, settings.ITEMS_FOR_PAGE)  # Show 25 contacts per page.
    page_number = request.GET.get("page")
    if page_number is None:
        page_number = 1
    page_obj = paginator.get_page(page_number)
    context["users"] = page_obj
    context["role"] = request.GET.get("role")
    return render(request, "administration/users_list.html", context=context)




@decorators.is_school_administrator
def edit_user(request, id):
    user = Account.objects.get(pk=id)
    if request.method == "GET":
        if request.user.role == "head_teacher":
            form = EditUserFormHeadTeacher(instance=user)
        else:
            form = EditUserForm(instance=user)
    else:
        if request.user.role == "head_teacher":
            form = EditUserFormHeadTeacher(request.POST, request.FILES, instance=user)
        else:
            form = EditUserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
        return redirect("/lk/users/list")
    return render(request, "administration/edit_user.html", {"form": form, "section": "users", "table_user": user})


@decorators.is_school_administrator
def avatar_remove(request, user):
    user = get_object_or_404(Account, pk=user)
    user.avatar = None
    user.save()
    return redirect(f"/lk/users/{user.pk}/edit")




@decorators.is_school_administrator
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


@decorators.is_school_administrator
def classrooms_list(request):
    classrooms = ClassRoom.objects.all()
    return render(request, "administration/classrooms.html", {"classrooms": classrooms, "section": "classrooms"})


@decorators.is_school_administrator
def classrooms_view(request, id):
    classrooms = get_object_or_404(ClassRoom, id=id)
    msgs = Message.objects.all().filter(room=classrooms.id)[0:25]
    return render(request, "administration/classroom_view.html",
                  {"classroom": classrooms, "msgs": msgs, "section": "classrooms"})
