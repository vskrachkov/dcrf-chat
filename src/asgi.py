import os

import django
import uvicorn
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()

from chat import consumers

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    path("ws/chat/room/", consumers.RoomConsumer.as_asgi()),
                ]
            )
        ),
    }
)

if __name__ == "__main__":
    uvicorn.run(application)