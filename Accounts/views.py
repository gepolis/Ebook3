from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import *
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from Accounts.forms import *
from .models import Account
from .forms import *


def register(request, mode):
    if request.user.is_authenticated:
        return redirect("/lk/")

    if request.method == "GET":
        if mode.lower() == "teacher":
            form = NewTeacherForm()
            return render(request, "auth/register.html", context={"form": form})
        if mode.lower() == "student":
            form = NewStudentForm()
            return render(request, "auth/register.html", context={"form": form})
        else:
            return HttpResponse("mode not found!")
        return render(request, "pages/auth/register.html")

    elif request.method == "POST":
        if mode.lower() == "teacher":
            form = NewTeacherForm(request.POST)
            if form.is_valid():
                user = form.save()
                user.save()
                login(request, user)
                messages.success(request, 'Вы успешно зарегистрировались!')
                return redirect("/lk/")
            else:
                messages.success(request, 'Ошибка!')
                return render(request, "auth/register.html", context={'form': form})

        if mode.lower() == "student":
            form = NewStudentForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                messages.success(request, 'Вы успешно зарегистрировались!')
                return redirect("/lk/")
            else:
                messages.success(request, 'Ошибка!')
                return render(request, "auth/register.html", context={"form": form})
        else:
            return HttpResponse("mode not found!")


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Вы успешно вошли!')
                return redirect("home")
            else:
                messages.warning(request, "Пользователь не найден.")
        else:
            messages.warning(request, "Пользователь не найден.")
    form = AuthenticationForm()
    return render(request=request, template_name="dashboard/login.html", context={"form": form})


@login_required
def logout_request(request):
    logout(request)
    messages.success(request, "Вы успешно вышли!")
    return redirect("/login")

@login_required
def setup(request):
    if request.method == "GET":
        if request.user.email is None or request.user.email == "":
            return render(request, "setup/email.html")
        elif request.user.second_name is None or request.user.second_name == "":
            return render(request, "setup/second_name.html")
        elif request.user.first_name is None or request.user.first_name == "":
            return render(request, "setup/first_name.html")
        elif request.user.middle_name is None or request.user.middle_name == "":
            return render(request, "setup/middle_name.html")
        else:
            return redirect("lk_main")
    else:
        t = request.POST['type']
        if t == "email":
            if not Account.objects.all().filter(email=request.POST['email']).exists():
                user = request.user
                user.email = request.POST['email']
                user.save()
                return redirect("setup")
            else:
                return HttpResponse(request.POST['email'])
        elif t == "fn":
            user = request.user
            user.first_name = request.POST['fn']
            user.save()
            return redirect("setup")
        elif t == "sn":
            user = request.user
            user.second_name = request.POST['sn']
            user.save()
            return redirect("setup")
        elif t == "mn":
            user = request.user
            user.middle_name = request.POST['mn']
            user.save()
            return redirect("setup")
        else:
            return redirect("lk_main")