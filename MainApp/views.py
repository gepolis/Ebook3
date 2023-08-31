from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import EventAddForm
from .models import Events
from django.contrib.auth.decorators import login_required
from Accounts.models import Account
import requests

def index(request):
    return render(request, "main.html")

def feedback(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        message = request.POST.get("message")
        print(name, email, phone, message)
        headers = {
                    #"Authorization": "MTA2Njg0NDI5OTUxMTIyMjI5NA.G8T_2D.HCBJ-AP1RhRXABiJhWfTS80SD1kJ8Gk4QHA6eo",
                    "Authorization": "Bot MTE0NTQ3MTMwMDcwMjMyNjkzNw.GQSnnl.SJt9a0Ul8kxCZVvnBgnXcdV3EcsS4tfnM_WnQU",
                    "content-encoding": "utf-8",
        }
        r = requests.post("https://discord.com/api/v8/channels/1146777719917531156/messages",
                            headers=headers, data={"content": f"Запрос, от {name}\n\nТел: {phone}\nПочта: {email}\n\n{message}"})
        print(r.json())
        return redirect("/")