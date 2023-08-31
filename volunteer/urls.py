"""
URL configuration for volunteer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include
from Accounts import views as accounts_views
from MainApp import views
from django.views.static import serve

urlpatterns = [
                  path('admin/', admin.site.urls),
                  # path('register/<str:mode>/', accounts_views.register),
                  path('login/', accounts_views.login_request),
                  path('logout/', accounts_views.logout_request, name="logout"),

                  path('lk/', include("PersonalArea.urls")),
                  path('setup/', accounts_views.setup, name="setup"),
                  path('', views.index),
                  path('auth/', accounts_views.auth, name="auth"),
                  path('auth/mosru/', accounts_views.auth_mos_ru, name="auth"),
                  path('auth/mosru/info/', accounts_views.mos_ru_info, name="auth"),
                  path('auth/register', accounts_views.register_request),
                  path('auth/login', accounts_views.login_request),
                  path('chatbot/', include("ChatBot.urls")),
                  path("user_activity/", accounts_views.user_activity),
                  path("feedback/", views.feedback)
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


def handler404(request, *args, **argv):
    return render(request, 'errors/404.html', status=404)


def handler500(request, *args, **argv):
    return render(request, 'errors/500.html', status=500)


def handler403(request, *args, **argv):
    return render(request, 'errors/403.html', status=403)


handler403 = handler403
handler500 = handler500
handler404 = handler404

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
