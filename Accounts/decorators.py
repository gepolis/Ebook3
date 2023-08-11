import functools

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.contrib import messages


def is_psychologist(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role == "psychologist":
                return view_func(request, *args, **kwargs)
            else:
                return PermissionDenied()
        else:
            return redirect("auth")

    return wrapper


def is_admin(view_func):
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role == "admin" or request.user.role == "director":
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied
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
                raise PermissionDenied
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
                raise PermissionDenied
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
                raise PermissionDenied
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
                raise PermissionDenied
        else:
            return redirect("auth")

    return wrapper
