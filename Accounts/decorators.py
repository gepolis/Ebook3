import functools

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages


def is_admin(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role == "admin":
                return view_func(request, *args, **kwargs)
            else:
                return render(request, "404.html")
        else:
            return redirect("auth")
    return wrapper

def has_role(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role is not None:
            return view_func(request, *args, **kwargs)
        else:
            return redirect("auth")

    return wrapper
def is_teacher(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role == "teacher":
                return view_func(request, *args, **kwargs)
            else:
                return render(request, "404.html")
        else:
            return redirect("auth")

    return wrapper


def is_student(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role == "student":
                return view_func(request, *args, **kwargs)
            else:
                return render(request, "404.html")
        else:
            return redirect("auth")

    return wrapper


def is_methodist(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role == "methodist":
                return view_func(request, *args, **kwargs)
            else:
                return render(request, "404.html")
        else:
            return redirect("auth")

    return wrapper


def is_admin_or_methodist(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role == "methodist" or request.user.role == "admin":
                return view_func(request, *args, **kwargs)
            else:
                return render(request, "404.html")
        else:
            return redirect("auth")

    return wrapper

