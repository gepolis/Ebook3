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



@decorators.is_student
def invite(request, classroom):
    classroom = ClassRoom.objects.get(uuid=classroom)
    classroom.member.add(request.user)
    classroom.save()
    messages.success(request, "Вы успешно вошли в класс")
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

@decorators.is_student
def student_invites(request):
    pass

