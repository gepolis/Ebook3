import datetime

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string

from MainApp.models import PsychologistSchedule


def calendar(request):
    return render(request, "psychologist/calendar.html")


def schedule_index(request):
    cal = render_to_string("psychologist/calendar.html", {"url": True, "classes": True})
    return render(request, "psychologist/schedule.html", {"section": "schedule", "cal": cal, "classes": False})


def schedule_date(request, d, m, y):
    cal = render_to_string("psychologist/calendar.html", {"url": False})
    ds = str(d)
    if len(ds) < 2:
        ds = f"0{d}"
    ms = str(m)
    if len(ms) < 2:
        ms = f"0{m}"
    date = f"{ds}.{ms}.{y}"
    datet = datetime.date(int(y), int(m), int(ds))
    classes = PsychologistSchedule.objects.all().filter(date=datet)
    return render(request, "psychologist/schedule_date_view.html",
                  {"section": "schedule", "date": date, "classes": classes, "cal": cal})


def edit_schedule(request):
    start = request.GET.get("start")
    end = request.GET.get("end")
    date = request.GET.get("date")
    id = request.GET.get("id")
    classes = get_object_or_404(PsychologistSchedule, pk=id)
    start = datetime.time(int(start.split(":")[0]), int(start.split(":")[1]))
    end = datetime.time(int(end.split(":")[0]), int(end.split(":")[1]))
    date = datetime.date(int(date.split(".")[2]), int(date.split(".")[1]), int(date.split(".")[0]))
    print(start, end, date)
    classes.start_time = start
    classes.end_time = end
    classes.date = date
    classes.save()
    return redirect(request.META.get("HTTP_REFERER"))


def has_month_classes(request, m, y):
    classes = PsychologistSchedule.objects.all().filter(date__month=m, date__year=y)
    data = {}
    for i in range(1,32):
        has = False
        for j in classes:
            if j.date.day == i:
                has = True
                break
        data[i] = has
    print(data)
    return JsonResponse(data)