"""
ASGI config for company project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

# Import your websocket routing patterns
from sections.chat.routing import websocket_urlpatterns as chat_urlpatterns
from sections.audio.routing import websocket_urlpatterns as audio_urlpatterns
from sections.notifications.routing import websocket_urlpatterns as notify_urlpatterns
from sections.blog.routing import websocket_urlpatterns as blog_urlpatterns
from sections.groups.routing import websocket_urlpatterns as groups_urlpatterns

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "company.settings")
django.setup()

# Combine all websocket routes
combined_websocket_urlpatterns = chat_urlpatterns + audio_urlpatterns + notify_urlpatterns + blog_urlpatterns + groups_urlpatterns

# ASGI application
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            combined_websocket_urlpatterns
        )
    ),
})
