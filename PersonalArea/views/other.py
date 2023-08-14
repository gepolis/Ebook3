from datetime import datetime
import io
from datetime import datetime

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.sessions.models import Session
from django.core.mail import send_mail

from . import aam
import xlsxwriter
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.formats import localize

from Accounts import decorators
from Accounts.models import Building, Connections
from MainApp.models import *
from PersonalArea.forms import *
from PersonalArea.models import Message
from PersonalArea.tasks import send

@login_required
@decorators.has_role
def index(request):
    for k, v in request.session.items():
        print(k, v)
    if request.user.role == "admin" or request.user.role == "director":
        item = Account.objects.all().filter(points__gt=0).order_by("-points")[:10]
        context = {
            "users": Account.objects.all().filter(is_superuser=False).count(),
            "events": Events.objects.all().count(),
            "reqs": EventsMembers.objects.all().filter(is_active=False).count(),
            "builds": Building.objects.all().count(),
            "students": item,
            "section": "index"
        }
        return render(request, "adminpanel/index.html", context)
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
        # return render(request, "chat.html")
        return render(request, "student/index.html", context=context)
    elif request.user.role == "methodist":
        context = {
            "section": "index"
        }
        return render(request, "methodist/index.html", context)
    elif request.user.role == "psychologist":
        context = {
            "section": "index"
        }
        return render(request, "psychologist/index.html", context)


def chat(request):
    if request.user.role in ["teacher", "student"]:
        room = request.user.get_classroom().id
    else:
        room = "staff"
    msgs = Message.objects.all().filter(room=room).order_by("date_added")
    return render(request, "chat.html", context={"msgs": msgs, "section": "chat", "room": room})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {
        'form': form
    })
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




@login_required
def events(request):
    if request.user.role == "teacher":
        if request.user.has_classroom():
            classroom = ClassRoom.objects.get(teacher=request.user)
            events = Events.objects.all().filter(classroom_number=classroom.classroom, start_date__lt=datetime.now(),
                                                 end_date__gt=timezone.now())
            return render(request, "teacher/events.html", {"events": events, "section": "events"})
        else:
            return redirect("/lk/classroom/create/")
    elif request.user.role == "student":
        if request.user.has_classroom():
            classroom = ClassRoom.objects.get(member=request.user)
            events = Events.objects.all().filter(classroom_number=classroom.classroom, start_date__lt=datetime.now(),
                                                 end_date__gt=timezone.now())
            return render(request, "student/events.html", {"events": events, 'section': 'events'})
        else:
            messages.warning(request, "Сначала вступите в класс, по приглашению от классного руковадителя.")
            return redirect("/lk/")
    else:
        return aam.events_list(request)


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
        wait = events.filter(pk=i.pk, start_date__gt=datetime.now()).exists()
        ended = events.filter(pk=i.pk, end_date__lt=datetime.now()).exists()
        # started = events.filter(pk=i.pk,end_date__gt=datetime.now(), start_date__lte=datetime.now()).exists()
        if wait:  # wait
            worksheet.write(f'D{m}', "Ожидание начала")
        elif ended:  # end
            worksheet.write(f'D{m}', "Завершено")
        else:  # start
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


@login_required
def event_detail(request, id):
    event = get_object_or_404(Events, pk=id)
    context = {
        "section": "events",
        "event": event,
        "report": PhotoReport.objects.all().filter(event=event, deleted=False),
        "end": Events.objects.all().filter(pk=event.pk, end_date__lt=datetime.now()).exists()
    }
    return render(request, "event_detail.html", context=context)

@login_required
def avatar_remove(request):
    user = request.user
    user.avatar = None
    user.save()
    return redirect("/lk/settings/")

@login_required
def devices(request):
    devices = Connections.objects.all().filter(user=request.user).order_by("-last_activity")
    return render(request, "devices.html", {"devices": devices})

    return None


def delete_device(request, device):
    connection = get_object_or_404(Connections, session_key=device)
    connection.delete()
    Session.objects.all().filter(session_key=device).delete()
    messages.success(request, "Устройство удалено.")
    return redirect("/lk/settings/security/devices")
