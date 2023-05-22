import functools

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages



def has_perm(perm):
    def decorator(func):
        def wrap(request, *args, **kwargs):
            if request.user.has_perm(perm, ignore_superuser=True):
                return func(request, *args, **kwargs)
            else:
                return redirect("/lk/")
        return wrap
    return decorator