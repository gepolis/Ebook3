import uuid
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
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

