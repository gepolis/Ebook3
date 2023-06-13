import functools

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages


def is_admin(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role == "admin":
            return view_func(request, *args, **kwargs)
        else:
            return render(request, "404.html")

    return wrapper

def has_role(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role is not None:
            return view_func(request, *args, **kwargs)
        else:
            return render(request, "404.html")

    return wrapper
def is_teacher(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role == "teacher":
            return view_func(request, *args, **kwargs)
        else:
            return render(request, "404.html")

    return wrapper


def is_student(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role == "student":
            return view_func(request, *args, **kwargs)
        else:
            return render(request, "404.html")

    return wrapper
