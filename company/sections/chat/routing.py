from django.urls import re_path
from .consumers import ChatConsumer, PrivateChatConsumer, ChatListConsumer, GroupListConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<slug>[^/]+)/$", ChatConsumer.as_asgi()),
    re_path(r"ws/private/(?P<receiver_username>\w+)/$", PrivateChatConsumer.as_asgi()),
    re_path(r'ws/chat-list/$', ChatListConsumer.as_asgi()),
    re_path(r'ws/group-list/$', GroupListConsumer.as_asgi()),
]
