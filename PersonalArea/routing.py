from django.urls import path

from . import custumers

websocket_urlpatterns = [
    path('ws/<str:classroom>/', custumers.ChatConsumer.as_asgi())
]