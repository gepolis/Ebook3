import uuid
from datetime import datetime
import time
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, Http404, FileResponse
from django.shortcuts import render, redirect
from Accounts.models import Account
from MainApp.models import Events, EventsMembers, ClassRoomsNumber, TeacherInviteEvent
from .forms import *
from Accounts.forms import NewBuildingForm
from Accounts.models import Building
from Accounts import decorators
import io
import xlsxwriter
from .models import Notications


def index(request):
    if request.user.role == "admin":
        context = {
            "users": Account.objects.all().count(),
            "events": Events.objects.all().count(),
            "reqs": EventsMembers.objects.all().filter(is_active=False).count(),
            "builds": Building.objects.all().count()
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
    context = {
        "count_users": users.count(),
        "count_staff": users.filter(role="admin").count() + users.filter(role="teacher").count(),
        "count_parents": users.filter(role="parent").count(),
        "count_students": users.filter(role="student").count()
    }
    if role is not None:
        users = users.filter(roles__name=role)
    context["users"] = users
    return render(request, "users_list.html", context=context)


@decorators.is_admin
def user_create(request):
    if request.method == "GET":
        form = NewUserForm()
    else:
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=True)
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
    return render(request, "edit_user.html", {"form": form})


@decorators.is_admin
def events_list(request, search=None):
    events = Events.objects.all().order_by("-id")
    context = {
        "count_events": events.count(),
        "count_requests": EventsMembers.objects.all().filter(is_active=True).count()
    }
    if search is None:
        context['events'] = events
    else:
        context['events'] = Events.objects.all().filter(name__icontains=search)
    return render(request, "events_list.html", context)


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
def events_view(request, id):
    event = Events.objects.get(pk=id)
    context = {
        "event": event,
        "reqs": event.volunteer.filter(is_active=False),
        "members": event.volunteer.filter(is_active=True)
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
    return render(request, "event_create.html", {"form": form})


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
    return render(request, "building_create.html", {"form": form})


@decorators.is_admin
def building_list(request):
    context = {
        "buildings": Building.objects.all().order_by("-id")
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


def read_notifications(request):
    t = round(time.time())
    notifications = Notications.objects.all().filter(user=request.user, created__lt=t)
    return JsonResponse({"message": "success", "user": request.user.id, "time": t, "viewed": notifications.count()})


def list_notifications(request):
    t = round(time.time())
    notifications = Notications.objects.all().filter(user=request.user)
    out = []
    for notification in notifications:
        out.append({
            'title': notification.title,
            'description': notification.description
        })
    return JsonResponse({"message": "success", "user": request.user.id, "time": t, "notification": out})
