import uuid
from datetime import datetime
import time
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, Http404, FileResponse
from django.shortcuts import render, redirect
from Accounts.models import Account
from MainApp.models import Events, EventsMembers, ClassRoomsNumber, TeacherInviteEvent
from django.utils.formats import localize

from .forms import *
from Accounts.forms import NewBuildingForm
from Accounts.models import Building
from Accounts import decorators
import io
import xlsxwriter
import pandas as pd
from .models import Notications


@decorators.has_role
def index(request):
    if request.user.role == "admin":
        item = Account.objects.all().filter(points__gt=0).order_by("-points")[:10]
        context = {
            "users": Account.objects.all().count(),
            "events": Events.objects.all().count(),
            "reqs": EventsMembers.objects.all().filter(is_active=False).count(),
            "builds": Building.objects.all().count(),
            "students": item,
            "section": "index"
        }
        return render(request, "index.html", context)
    elif request.user.role == "teacher":
        return render(request, "teacher/index.html")
    elif request.user.role == "student":
        return render(request, "student/index.html")


@decorators.is_admin
def view_user(request, id):
    user = Account.objects.get(pk=id)
    return render(request, "view_user.html", {"view_user": user})


@decorators.is_admin
def users_list(request, role=None):
    users = Account.objects.all().order_by("-id")
    create_user_form = NewUserForm()
    context = {
        "count_users": users.count(),
        "count_staff": users.filter(role="admin").count() + users.filter(role="teacher").count(),
        "count_parents": users.filter(role="parent").count(),
        "count_students": users.filter(role="student").count(),
        "create_user_form": create_user_form,
        "section": "users"
    }
    if role is not None:
        users = users.filter(roles__name=role)
    context["users"] = users
    return render(request, "users_list.html", context=context)


@decorators.is_admin
def user_create(request):
    if request.method == "GET":
        return redirect("/lk/users/list")
    else:
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=True)
            print("valid")
        else:
            print(form.errors)
        return redirect("/lk/users/list")
    return render(request, "user_create.html", {"form": form})


@decorators.is_admin
def edit_user(request, id):
    user = Account.objects.get(pk=id)
    if request.method == "GET":
        form = EditUserForm(instance=user)
    else:
        form = EditUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
        return redirect("/lk/users/list")
    return render(request, "edit_user.html", {"form": form, "section": "users"})


@login_required
def edit_profile(request):
    if request.method == "GET":
        form = EditProfileForm(instance=request.user)
    else:
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
        else:
            return HttpResponse(form.errors)
        return redirect("/lk/settings/")
    return render(request, "settings.html", {"form": form})


@decorators.is_admin
def events_list(request, search=None):
    events = Events.objects.all().filter(archive=False).order_by("-id")
    context = {
        "count_events": events.count(),
        "count_requests": EventsMembers.objects.all().filter(is_active=True).count(),
        "section": "events"
    }
    if search is None:
        context['events'] = events
    else:
        context['events'] = Events.objects.all().filter(name__icontains=search)
    return render(request, "events_list.html", context)


@decorators.is_admin
def give_points(request, id):
    event = Events.objects.get(pk=id)
    volunteers = event.volunteer.all().filter(points=None)
    if request.method == "POST":
        user = request.POST.get("user")
        points = request.POST.get("points")
        if user is not None and points is not None:
            volunteer = volunteers.get(pk=user)
            volunteer.points = points
            volunteer.save()
            user_account = volunteer.user
            user_account.points += int(points)
            user_account.save()
            return redirect(f"/lk/events/{event.pk}/points/give")
    else:
        return render(request, "give_points.html", {"event": event, "volunteers": volunteers, "section": "events"})


@decorators.is_admin
def events_archive_list(request):
    events = Events.objects.all().filter(archive=True).order_by("-id")
    context = {
        "count_events": events.count(),
        "count_requests": EventsMembers.objects.all().filter(is_active=True).count(),
        "events": events,
        "section": "events"
    }
    return render(request, "events_archive_list.html", context)


@decorators.is_admin
def event_export(request, id):
    event = Events.objects.get(pk=id)
    buffer = io.BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', 'ФИО')
    worksheet.write('B1', 'Баллов')
    m = 1
    points = 0
    for i in event.volunteer.all():
        m += 1
        if i.points is not None:
            points += i.points
            worksheet.write(f'B{m}', i.points)
        else:
            worksheet.write(f'B{m}', 0)
        worksheet.write(f'A{m}', i.user.full_name())
    worksheet.write(f'A{m + 1}', "Всего")
    worksheet.write(f'B{m + 1}', points)
    worksheet.autofit()
    workbook.close()
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename=f'{event.name}.xlsx')


@decorators.is_admin
def event_archive(request, id):
    event = Events.objects.get(pk=id)
    event.archive = True
    event.save()
    return redirect("/lk/events/list/")


@decorators.is_admin
def event_unarchived(request, id):
    event = Events.objects.get(pk=id)
    event.archive = False
    event.save()
    return redirect("/lk/events/archive/")


@decorators.is_admin
def events_view(request, id):
    event = Events.objects.get(pk=id)
    context = {
        "event": event,
        "reqs": event.volunteer.filter(is_active=False),
        "members": event.volunteer.filter(is_active=True),
        "section": "events"
    }
    return render(request, "event_view.html", context)


@decorators.is_admin
def event_create(request):
    if request.method == "GET":
        form = EventAddForm()
    else:
        form = EventAddForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=True)
        else:
            return HttpResponse(form.errors)
        return redirect("/lk/events/list")
    return render(request, "event_create.html", {"form": form, "section": "events"})


@decorators.is_admin
def event_accept_user(request, id, user):
    user = EventsMembers.objects.get(id=user)
    user.is_active = True
    user.save()
    return redirect(f"/lk/events/{id}/view")


@decorators.is_admin
def event_reject_user(request, id, user):
    user = EventsMembers.objects.get(id=user)
    user.delete()
    return redirect(f"/lk/events/{id}/view")


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
    return render(request, "building_create.html", {"form": form, "section": "building"})


@decorators.is_admin
def building_list(request):
    context = {
        "buildings": Building.objects.all().order_by("-id"),
        "section": "building"
    }
    return render(request, "buildings_list.html", context=context)


def handler404(request, *args, **argv):
    return render(request, '404.html', status=404)


def handler500(request, *args, **argv):
    return render(request, '500.html', status=500)


@decorators.is_teacher
def create_classroom(request):
    if ClassRoom.objects.all().filter(teacher=request.user).exists():
        return redirect("/lk/")
    if request.method == "GET":
        form = NewClassRoom()
    else:
        form = NewClassRoom(request.POST)
        if form.is_valid():
            classroom = form.save(commit=False)
            classroom.teacher = request.user
            classroom.save()
        return redirect("/lk/")
    return render(request, "teacher/create_classroom.html", {"form": form})


@decorators.is_teacher
def create_invite(request):
    if ClassRoom.objects.all().filter(teacher=request.user).exists():
        classroom = ClassRoom.objects.get(teacher=request.user)
        return render(request, "teacher/invite.html", {"invite_url": classroom.invite_url()})
    else:
        return redirect("/lk/classroom/create/")


@decorators.is_teacher
def update_invite(request):
    if ClassRoom.objects.all().filter(teacher=request.user).exists():
        classroom = ClassRoom.objects.get(teacher=request.user)
        classroom.uuid = uuid.uuid4()
        classroom.save()
        return redirect("/lk/classroom/invite/create/")
    else:
        return redirect("/lk/classroom/create/")


@decorators.is_teacher
def invite_classroom_event(request, id):
    if ClassRoom.objects.all().filter(teacher=request.user).exists():
        classroom = ClassRoom.objects.get(teacher=request.user)
        events = Events.objects.get(pk=id)
        for member in classroom.member.all():
            i = TeacherInviteEvent(user=member, classroom=classroom, event=events)
            i.save()
        messages.success(request, "Вы успешно пригласили класс на мероприятие.")
        return redirect("/lk/events/")
    else:
        return redirect("/lk/classroom/create/")


@decorators.is_teacher
def classroom_students(request):
    if ClassRoom.objects.all().filter(teacher=request.user).exists():
        classroom = ClassRoom.objects.get(teacher=request.user)
        members = classroom.member.all()
        return render(request, "teacher/students.html", {"members": members})
    else:
        return redirect("/lk/classroom/create/")


@decorators.is_teacher
def classroom_view_student(request, user):
    if ClassRoom.objects.all().filter(teacher=request.user).exists():
        classroom = ClassRoom.objects.get(teacher=request.user)
        if classroom.member.all().filter(pk=user).exists():
            user = classroom.member.get(pk=user)
            events = Events.objects.all().filter(volunteer__user=user)
            return render(request, "teacher/view_student.html", {"student": user, "events": events})
        else:
            return redirect("/lk/classroom/students/")
    else:
        return redirect("/lk/classroom/create/")


@decorators.is_student
def invite(request, classroom):
    classroom = ClassRoom.objects.get(uuid=classroom)
    classroom.member.add(request.user)
    classroom.save()
    messages.success(request, "Вы успешно вошли в класс")
    return redirect("/lk/")


def events(request):
    if request.user.role == "teacher":
        classroom = ClassRoom.objects.get(teacher=request.user)
        events = Events.objects.all().filter(classroom_number=ClassRoomsNumber.objects.get(value=classroom.classroom))
        return render(request, "teacher/events.html", {"events": events})
    elif request.user.role == "student":
        classroom = ClassRoom.objects.get(member=request.user)
        events = Events.objects.all().filter(classroom_number=ClassRoomsNumber.objects.get(value=classroom.classroom))
        return render(request, "student/events.html", {"events": events})


@decorators.is_student
def event_request(request, event):
    event = Events.objects.get(pk=event)
    member = EventsMembers(user=request.user)
    member.save()
    event.volunteer.add(member)
    messages.success(request, "Вы успешно подали заявку на мероприятие")
    return redirect("/lk/events/")


@decorators.is_student
def my_events(request):
    events = Events.objects.all().filter(volunteer__user=request.user)
    wait = events.filter(start_date__gt=datetime.now())
    ended = events.filter(end_date__lt=datetime.now())
    started = events.filter(end_date__gt=datetime.now(), start_date__lte=datetime.now())
    return render(request, "student/my_events.html", {"started": started, "ended": ended, "wait": wait})

@login_required
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
