from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import EventAddForm
from .models import Events
from django.contrib.auth.decorators import login_required
from Accounts.models import Account


def home(request):
    return render(request, "pages/home.html")


@login_required
def add_event(request):
    if request.method == "GET":
        form = EventAddForm()
        return render(request, "dashboard/create_event.html", context={"form": form})
    elif request.method == "POST":
        form = EventAddForm(request.POST)
        if form.is_valid():
            event = form.save(commit=True)
            messages.success(request, 'Вы успешно создали мероприятие!')
            return redirect("home")
        return render(request, "pages/events/add.html", context={"form": form})


def test(request, name):
    if request.user.is_staff or 1 == 1:
        if name == "otp":
            if request.method == "GET":
                return render(request, f"dashboard/otp.html")
            else:
                print(request.POST)
                return HttpResponse("http")
        else:
            return render(request, f"dashboard/{name}.html")
    else:
        return render(request, "dashboard/errors/403.html")


@login_required
def get_event(request, id):
    event = Events.objects.get(pk=id)
    return render(request, "pages/events/event.html", context={"event": event})


@login_required
def lk(request, arg=None, arg_two=None, arg_three=None):
    user = request.user
    rank = "Гость"
    color = "secondary"
    type = ""
    if 1==1:
        rank = "Администратор"
        color = "danger"
        context = {"rank": rank,
                   "color": color,
                   "admins":len(Account.objects.all()),
                   "teachers": len(Account.objects.all()),
                   "students": len(Account.objects.all()),
                   "parents": len(Account.objects.all())
                   }

        if arg is None:
            context['all_users'] = len(Account.objects.all())
            return render(request, f"lk/administrator/index.html", context=context)
        elif arg == "test":
            p=False
            roles = request.user.roles
            for r in roles:
                if r.perms.all().filter(name="lk.admin").exists():
                   p=True
            context['perm'] = p
            return render(request, f"lk/administrator/test.html", context=context)
        elif arg == "users":
            if arg_two is None:
                context['users'] = Account.objects.all().order_by('-id')[:20]
                context['active_all'] = True
                return render(request, f"lk/administrator/users.html", context=context)

            elif arg_two=="students":
                context['users'] = Account.objects.all().filter(is_student=True).order_by('-id')[:20]
                context['active_students']=True
                return render(request, f"lk/administrator/users.html", context=context)
            elif arg_two=="teachers":
                context['users'] = Account.objects.all().filter(is_teacher=True).order_by('-id')[:20]
                context['active_teachers'] = True
                return render(request, f"lk/administrator/users.html", context=context)
            elif arg_two=="parents":
                context['users'] = Account.objects.all().filter(is_parent=True).order_by('-id')[:20]
                context['active_parents'] = True
                return render(request, f"lk/administrator/users.html", context=context)
            elif arg_two=="admins":
                context['users'] = Account.objects.all().filter(is_admin=True).order_by('-id')[:20]
                context['active_admins'] = True
                return render(request, f"lk/administrator/users.html", context=context)
            elif arg_three is not None:
                if arg_three == "delete":
                    user = Account.objects.get(pk=int(arg_two))
                    user.delete()
                    return redirect("/lk/users")
    elif 1==1:
        rank = "Учитель"
        color = "primary"
    elif 1==1:
        rank = "Родитель"
        color = "primary"
    elif 1==1:
        rank = "Учащийся"
        color = "primary"
        type = "student"


@login_required
def event_register(request, id):
    if request.user.is_volunteer:
        if not Events.objects.get(pk=id).volunteer.filter(pk=request.user.pk).exists():
            event = Events.objects.get(pk=id)
            event.volunteer.add(request.user)
            messages.success(request, "Вы подали заявку на участие.")

    return redirect(f"/events/{id}")
