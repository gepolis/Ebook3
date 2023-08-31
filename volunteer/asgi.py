

import os

from django.core.asgi import get_asgi_application

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

import PersonalArea.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'volunteer.settings')

application = ProtocolTypeRouter({
    "https": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            PersonalArea.routing.websocket_urlpatterns
        )
    )
})
