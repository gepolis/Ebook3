import random
from datetime import datetime

import django_user_agents.utils
import dnevniklib
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import *
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone

from .models import Account
from .forms import *
from .models import *
from .utils import get_token
from MainApp.models import ClassRoom


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def add_connection(request):
    ip = get_client_ip(request)
    ua_string = request.META.get('HTTP_USER_AGENT', '')
    print("----")
    print(ua_string)
    print("----")
    ua = django_user_agents.utils.parse(ua_string)

    Connections.objects.create(ip=ip, user=request.user, session_key=request.session.session_key,
                               device_system=request.user_agent.os.family,
                               device_browser=request.user_agent.browser.family).save()


def register_request(request):
    add_connection(request)
    if request.user.is_authenticated:
        return redirect("/lk/")

    elif request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.save()
            login(request, user)
            add_connection(request)
            messages.success(request, 'Вы успешно зарегистрировались!')
            return redirect("/lk/")
        else:
            messages.success(request, f'Ошибка({form.errors})!')
            return redirect("/auth/?m=reg")
    else:
        return HttpResponse("m")


def auth(request):
    if request.user.is_authenticated:
        return redirect("/lk/")
    context = {
        "register_form": NewUserForm(),
        "login_form": AccountSignInForm()
    }
    return render(request, "auth.html", context=context)


def auth_mos_ru(request):
    #messages.error(request, "Авторизация через mos.ru временно не работает, пожалуйста, используйте другой способ авторизации или попробуйте позже.")
    #return redirect("/auth/")
    if request.user.is_authenticated:
        return redirect("/lk/")

    if request.method == "GET":
        if request.GET.get("token"):
            return mos_ru_login(request, request.GET.get("token"))
        else:
            context = {
                "login_form": AccountMosRuForm()
            }
            return render(request, "mos_ru_auth.html", context=context)
    else:
        form = AccountMosRuForm(request.POST)
        context = {"login_form": form}
        if form.is_valid():
            # print(form.cleaned_data)
            token = get_token(form.cleaned_data["login"], form.cleaned_data['password'])
            if token:
                return mos_ru_login(request, token)
            else:
                messages.error(request, "Неверный логин или пароль.")
                return render(request, "mos_ru_auth.html", context=context)
        else:
            return HttpResponse("f")


def mos_ru_login(request, token):
    user = dnevniklib.User(token=token)
    school = dnevniklib.School(user=user)
    # print(user.data_about_user)
    if school.get_info_about_school()['short_name'] == "ГБОУ Школа № 1236":
        if not Account.objects.all().filter(email=user.email).exists():

            username = f"user_{Account.objects.all().count()}"
            auth_user = Account(email=user.email, username=username, first_name=user.first_name,
                                second_name=user.last_name, middle_name=user.middle_name,
                                role=user.data_about_user['profile']['type'],
                                date_of_birth=user.data_about_user['profile']['birth_date'], password="mos.ru")
            auth_user.save()
            login(request, auth_user)

            if user.type == "student":
                class_room_user = user.class_name.split("-")
                classroom = ClassRoom.objects.all().filter(parallel=class_room_user[1],
                                                           classroom=int(class_room_user[0]))
                if classroom.exists():
                    classroom = classroom.first()
                    classroom.member.add(auth_user)
                else:
                    classroom = ClassRoom(parallel=class_room_user[1], classroom=int(class_room_user[0]))
                    classroom.save()
                    classroom.member.add(auth_user)
                    classroom.save()
                c = redirect("/lk/")
                c.set_cookie("token", token, max_age=86400 * 38)  # 38 дней
                return c

        else:
            auth_user = Account.objects.get(email=user.email)
            login(request, auth_user)
        return redirect("/lk/")
    return HttpResponse(user.data_about_user)


def login_request(request):
    if request.user.is_authenticated:
        return redirect("/lk/")

    if request.method == "POST":
        form = AccountSignInForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
                ip = get_client_ip(request)
                if not Connections.objects.all().filter(ip=get_client_ip(request), user=user).exists():
                    add_connection(request)
                else:
                    add_connection(request)
                messages.success(request, 'Вы успешно вошли!')
                return redirect("/lk/")
            else:
                messages.warning(request, "Пользователь не найден.")
        else:
            messages.warning(request, "Пользователь не найден.")
    form = AuthenticationForm()
    return redirect("/auth/?m=reg")


@login_required
def logout_request(request):
    Connections.objects.all().filter(user=request.user, session_key=request.session.session_key).delete()
    logout(request)
    messages.success(request, "Вы успешно вышли!")
    c = redirect("/login")
    c.set_cookie("token", "", max_age=0)
    return c


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
            return redirect("/")
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
            return redirect("/")


@login_required
def user_activity(request):
    if Connections.objects.all().filter(user=request.user, session_key=request.session.session_key).exists():
        con = Connections.objects.get(user=request.user, session_key=request.session.session_key)
        if request.COOKIES.get("activity") is None:
            print("update")
            con.last_activity = datetime.now()
            con.save()
            j = JsonResponse({"status": "ok", "code": 1}, status=200, safe=False)
            j.set_cookie("activity", "ok", max_age=60)
        else:
            j = JsonResponse({"status": "cancel", "code": 2}, status=200, safe=False)
            print("cancel")
        j.set_cookie("welcome_screen", "", max_age=60*30)  # 30 min - 60*30
        return j
    else:
        return JsonResponse({"status": "error"}, status=400, safe=False)

def mos_ru_info(request):
    return render(request, "mos_ru_auth_info.html")