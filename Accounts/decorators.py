import functools

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages


def is_admin(view_func):
    """
        this decorator ensures that a user is not logged in,
        if a user is logged in, the user will get redirected to
        the url whose view name was passed to the redirect_url parameter
    """

    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role == "admin":
            return view_func(request, *args, **kwargs)
        else:
            return render(request,"404.html")

    return wrapper

def is_teacher(view_func):
    """
        this decorator ensures that a user is not logged in,
        if a user is logged in, the user will get redirected to
        the url whose view name was passed to the redirect_url parameter
    """

    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role == "teacher":
            return view_func(request, *args, **kwargs)
        else:
            return render(request,"404.html")

    return wrapper


def is_student(view_func):
    """
        this decorator ensures that a user is not logged in,
        if a user is logged in, the user will get redirected to
        the url whose view name was passed to the redirect_url parameter
    """

    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.role == "student":
            return view_func(request, *args, **kwargs)
        else:
            return render(request,"404.html")

    return wrapper
