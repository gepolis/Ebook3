import uuid
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.conf import settings
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



@decorators.is_admin_or_methodist
def events_list(request, search=None):
    if request.user.role == "methodist":
        categories = EventCategory.objects.all().filter(methodists=request.user)
        events = Events.objects.all().filter(archive=False, category__in=categories).order_by("-id")
    else:
        events = Events.objects.all().filter(archive=False).order_by("-id")
    context = {
        "count_events": events.count(),
        "count_requests": EventsMembers.objects.all().filter(is_active=False, volunteers__in=events).count(),
        "section": "events"
    }
    paginator = Paginator(events, settings.ITEMS_FOR_PAGE)
    page_number = request.GET.get("page")
    if page_number is None:
        page_number = 1
    page_obj = paginator.get_page(page_number)
    context["events"] = page_obj
    return render(request, "aam/events_list.html", context)

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
        return render(request, "aam/give_points.html", {"event": event, "volunteers": volunteers, "section": "events"})


@decorators.is_admin_or_methodist
def events_archive_list(request):
    if request.user.role == "methodist":
        categories = EventCategory.objects.all().filter(methodists=request.user)
        events = Events.objects.all().filter(archive=True, category__in=categories).order_by("-id")
    else:
        events = Events.objects.all().filter(archive=True).order_by("-id")
    context = {
        "count_events": events.count(),
        "count_requests": EventsMembers.objects.all().filter(is_active=True, volunteers__in=events).count(),
        "section": "events"
    }
    paginator = Paginator(events, settings.ITEMS_FOR_PAGE)  # Show 25 contacts per page.
    page_number = request.GET.get("page")
    if page_number is None:
        page_number = 1
    page_obj = paginator.get_page(page_number)
    context["events"] = page_obj
    return render(request, "aam/events_archive_list.html", context)

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
        "wait": Events.objects.all().filter(pk=event.pk,start_date__gt=timezone.now()).exists(),
        "end":  Events.objects.all().filter(pk=event.pk,end_date__lt=timezone.now()).exists()
    }
    return render(request, "aam/event_view.html", context)



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
                return render(request, "aam/event_create.html", {"form": form, "section": "events"})
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
                return render(request, "aam/event_create.html", {"form": form, "section": "events"})
            return redirect("/lk/events/list")
    else:
        return redirect("/lk/")
    return render(request, "aam/event_create.html", {"form": form, "section": "events"})


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

@decorators.is_admin_or_methodist
def photo_report(request, id):

    event = get_object_or_404(Events, pk=id)
    context = {
        "section": "events",
        "event": event,
        "report": PhotoReport.objects.all().filter(event=event, deleted=False)
    }
    if request.method == "GET":
        context['form']=UploadPhotoReport()
        return render(request,"aam/photo_report.html",context)
    else:
        form = UploadPhotoReport(request.POST, request.FILES)
        files = request.FILES.getlist("file")
        for f in files:
            if f.name.split(".")[-1] in ["jpg", "jpeg", "png", "gif"]:
                p = PhotoReport(image=f, event=event, author=request.user)
                p.save()
        return redirect(f"/lk/events/{event.pk}/photo/report")

@decorators.is_admin_or_methodist
def photo_delete(request, id,image):
    photo = get_object_or_404(PhotoReport, pk=image)
    photo.delete()
    return redirect(f"/lk/events/{photo.event.pk}/photo/report")