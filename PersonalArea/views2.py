import uuid
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from Accounts.models import Account
from MainApp.models import *
from django.utils.formats import localize

from .forms import *
from Accounts.forms import NewBuildingForm
from Accounts.models import Building
from Accounts import decorators
import io
import xlsxwriter
import pandas as pd
from .models import Notications, Message


@login_required
@decorators.has_role
def index(request):
    if request.user.role == "admin" or request.user.role == "director":
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

        context = {
            "section": "index"
        }
        if request.user.has_classroom():
            classroom = ClassRoom.objects.get(teacher=request.user)
            item = classroom.member.all()
            context['students'] = item
        return render(request, "teacher/index.html", context=context)
    elif request.user.role == "student":
        context = {
            "section": "index"
        }
        #return render(request, "chat.html")
        return render(request, "student/index.html", context=context)
    elif request.user.role == "methodist":
        context = {
            "section": "index"
        }
        return render(request, "methodist/index.html", context)

def chat(request):
    msgs = Message.objects.all().filter(room=str(request.user.get_classroom().id))[0:25]
    return render(request, "chat.html", context={"msgs": msgs,"section":"chat"})

@decorators.is_admin
def view_user(request, id):
    user = Account.objects.get(pk=id)
    return render(request, "view_user.html", {"view_user": user})


@decorators.is_admin
def users_list(request, role=None):
    users = Account.objects.all().filter(is_superuser=False).order_by("-id")
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
            return render(request, "settings.html", {"form": form})
        return redirect("/lk/settings/")
    return render(request, "settings.html", {"form": form})

@decorators.is_admin_or_methodist
def events_list(request, search=None):
    if request.user.role == "admin" or request.user.role == "director":
        events = Events.objects.all().filter(archive=False).order_by("-id")
        context = {
            "count_events": events.count(),
            "count_requests": EventsMembers.objects.all().filter(is_active=False).count(),
            "section": "events"
        }
        if search is None:
            context['events'] = events
        else:
            context['events'] = Events.objects.all().filter(name__icontains=search)
        return render(request, "events_list.html", context)
    elif request.user.role == "methodist":
        categories = EventCategory.objects.all().filter(methodists=request.user)
        events = Events.objects.all().filter(archive=False, category__in=categories).order_by("-id")
        context = {
            "count_events": events.count(),
            "count_requests": EventsMembers.objects.all().filter(is_active=True).count(),
            "section": "events"
        }
        if search is None:
            context['events'] = events
        else:
            context['events'] = Events.objects.all().filter(name__icontains=search)
        return render(request, "methodist/events_list.html", context)
@decorators.is_admin_or_methodist
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


@decorators.is_admin_or_methodist
def events_archive_list(request):
    if request.user.role == "admin" or request.user.role == "director":
        events = Events.objects.all().filter(archive=True).order_by("-id")
        context = {
            "count_events": events.count(),
            "count_requests": EventsMembers.objects.all().filter(is_active=False).count(),
            "section": "events",
            "events": events
        }
        return render(request, "events_archive_list.html", context)
    elif request.user.role == "methodist":
        categories = EventCategory.objects.all().filter(methodists=request.user)
        events = Events.objects.all().filter(archive=True, category__in=categories).order_by("-id")
        context = {
            "count_events": events.count(),
            "count_requests": EventsMembers.objects.all().filter(is_active=True).count(),
            "section": "events",
            "events": events
        }
        return render(request, "methodist/events_archive_list.html", context)

@decorators.is_admin_or_methodist
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


@decorators.is_admin_or_methodist
def event_archive(request, id):
    event = Events.objects.get(pk=id)
    event.archive = True
    event.save()
    return redirect("/lk/events/list/")


@decorators.is_admin_or_methodist
def event_unarchived(request, id):
    event = Events.objects.get(pk=id)
    event.archive = False
    event.save()
    return redirect("/lk/events/archive/")

@decorators.is_admin_or_methodist
def events_view(request, id):
    if request.user.role == "admin" or request.user.role == "director":
        event = Events.objects.get(pk=id)

    elif request.user.role == "methodist":
        categories = EventCategory.objects.all().filter(methodists=request.user)
        if Events.objects.all().filter(pk=id, category__in=categories).exists():
            event = Events.objects.get(pk=id)
        else:
            return redirect("events_list")
    context = {
        "event": event,
        "reqs": event.volunteer.filter(is_active=False),
        "members": event.volunteer.filter(is_active=True),
        "section": "events",
        "wait": Events.objects.all().filter(pk=event.pk,start_date__lt=datetime.now()).exists(),
        "end":  Events.objects.all().filter(pk=event.pk,end_date__gt=datetime.now()).exists()
    }
    return render(request, "event_view.html", context)



@login_required
def event_create(request):
    if request.user.role == "admin" or request.user.role == "director":
        if request.method == "GET":
            form = EventAddForm()
        else:
            form = EventAddForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                form.save_m2m()
            else:
                return render(request, "event_create.html", {"form": form, "section": "events"})
            return redirect("/lk/events/list")
    elif request.user.role == "methodist":
        if request.method == "GET":
            form = EventAddFormMethodist(loggedin_user=request.user)
        else:
            form = EventAddFormMethodist(None, request.POST, request.FILES)
            if form.is_valid():
                form.save()
                form.save_m2m()
            else:
                return render(request, "event_create.html", {"form": form, "section": "events"})
            return redirect("/lk/events/list")
    else:
        return redirect("/lk/")
    return render(request, "event_create.html", {"form": form, "section": "events"})


@decorators.is_admin_or_methodist
def event_accept_user(request, id, user):
    user = EventsMembers.objects.get(id=user)
    user.is_active = True
    user.save()
    return redirect(f"/lk/events/{id}/view")


@decorators.is_admin_or_methodist
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
            if form.unique():
                classroom = form.save(commit=False)
                classroom.teacher = request.user
                classroom.save()
            else:
                messages.error(request,"Данный класс уже существует. Если вы являетесь классным руководителем класса который уже существует, обратитесь к администрации.")
                return render(request,"teacher/create_classroom.html", {"form": form, "section": "classroom"})
        return redirect("/lk/")
    return render(request, "teacher/create_classroom.html", {"form": form, "section": "classroom"})


@decorators.is_teacher
def create_invite(request):
    if ClassRoom.objects.all().filter(teacher=request.user).exists():
        classroom = ClassRoom.objects.get(teacher=request.user)
        return render(request, "teacher/invite.html", {"uuid": classroom.uuid, "section": "classroom"})
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
        return render(request, "teacher/students.html", {"members": members, "section": "classroom"})
    else:
        return redirect("/lk/classroom/create/")


@decorators.is_teacher
def classroom_view_student(request, user):
    if ClassRoom.objects.all().filter(teacher=request.user).exists():
        classroom = ClassRoom.objects.get(teacher=request.user)
        if classroom.member.all().filter(pk=user).exists():
            user = classroom.member.get(pk=user)
            events = Events.objects.all().filter(volunteer__user=user)
            return render(request, "teacher/view_student.html", {"student": user, "events": events, "section": "classroom"})
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

@login_required
def events(request):
    if request.user.role == "teacher":
        if request.user.has_classroom():
            classroom = ClassRoom.objects.get(teacher=request.user)
            events = Events.objects.all().filter(classroom_number=classroom.classroom, start_date__lt=datetime.now(), end_date__gt=datetime.now())
            return render(request, "teacher/events.html", {"events": events, "section": "events"})
        else:
            return redirect("/lk/classroom/create/")
    elif request.user.role == "student":
        if request.user.has_classroom():
            classroom = ClassRoom.objects.get(member=request.user)
            events = Events.objects.all().filter(classroom_number=classroom.classroom, start_date__lt=datetime.now(), end_date__gt=datetime.now())
            return render(request, "student/events.html", {"events": events, 'section': 'events'})
        else:
            messages.warning(request, "Сначала вступите в класс, по приглашению от классного руковадителя.")
            return redirect("/lk/")

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
    return render(request, "student/my_events.html", {"started": started, "ended": ended, "wait": wait, 'section': 'my_events'})

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
    return render(request, "category_list.html", {"categories": categories,"form": form,"section": "events"})

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

@login_required
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
        return render(request, "edit_category.html", {"section": "events", "form": form})

@decorators.is_student
def student_invites(request):
    pass

@login_required
def all_events(request):
    e = Events.objects.all()
    mode = request.GET.get("mode")
    if mode == "my":
        em = EventsMembers.objects.all().filter(user=request.user)
        e = e.filter(volunteer__in=em)
    elif mode == "student":
        student = request.GET.get("student")
        if student is not None:
            student = Account.objects.get(pk=student)
            em = EventsMembers.objects.all().filter(user=student)
            e = e.filter(volunteer__in=em)
        else:
            return JsonResponse({}, safe=False)
    out = []
    for event in e:
        out.append({
            'title': event.name,
            'id': event.id,
            'start': event.start_date.strftime("%m/%d/%Y, %H:%M:%S"),
            'end': event.end_date.strftime("%m/%d/%Y, %H:%M:%S"),
        })

    return JsonResponse(out, safe=False)

@login_required
def classroom_view_export(request, user):
    user = Account.objects.get(pk=user)
    events = Events.objects.all().filter(volunteer__in=EventsMembers.objects.all().filter(user=user, is_active=True))
    buffer = io.BytesIO()
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', 'Название')
    worksheet.write('B1', 'Начало')
    worksheet.write('C1', 'Конец')
    worksheet.write('D1', 'Статус')
    worksheet.write('E1', 'Баллов')
    m = 1
    points = 0
    for i in events:
        m += 1
        wait = events.filter(pk=i.pk,start_date__gt=datetime.now()).exists()
        ended = events.filter(pk=i.pk,end_date__lt=datetime.now()).exists()
        #started = events.filter(pk=i.pk,end_date__gt=datetime.now(), start_date__lte=datetime.now()).exists()
        if wait: # wait
            worksheet.write(f'D{m}', "Ожидание начала")
        elif ended: #end
            worksheet.write(f'D{m}', "Завершено")
        else: #start
            worksheet.write(f'D{m}', "Началось")

        if i.volunteer.get(user=user).points is not None:
            points += i.volunteer.get(user=user).points
            worksheet.write(f'E{m}', i.volunteer.get(user=user).points)
        else:
            worksheet.write(f"E{m}", "-")
        worksheet.write(f"B{m}", localize(i.start_date))
        worksheet.write(f"C{m}", localize(i.end_date))
        worksheet.write(f'A{m}', i.name)
    worksheet.autofit()
    workbook.close()
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename=f'{user.full_name()}.xlsx')

@decorators.is_admin_or_methodist
def photo_report(request, id):

    event = get_object_or_404(Events, pk=id)
    context = {
        "section": "events",
        "event": event,
        "report": PhotoReport.objects.all().filter(event=event)
    }
    if request.method == "GET":
        context['form']=UploadPhotoReport()
        return render(request,"photo_report.html",context)
    else:
        form = UploadPhotoReport(request.POST, request.FILES)
        files = request.FILES.getlist("file")
        for f in files:
            p = PhotoReport(image=f, event=event)
            p.save()
        return redirect(f"/lk/events/{event.pk}/photo/report")
@login_required
def event_detail(request, id):
    event = get_object_or_404(Events, pk=id)
    context = {
        "section": "events",
        "event": event,
        "report": PhotoReport.objects.all().filter(event=event),
        "end": Events.objects.all().filter(pk=event.pk, end_date__lt=datetime.now()).exists()
    }
    return render(request,"event_detail.html", context=context)