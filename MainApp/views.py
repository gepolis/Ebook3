from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import EventAddForm
from .models import Events
from django.contrib.auth.decorators import login_required
from Accounts.models import Account


def index(request):
    return render(request, "main.html")

