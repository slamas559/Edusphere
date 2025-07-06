from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/audio/room/(?P<room_name>\w+)/$', consumers.GroupAudioConsumer.as_asgi()),
]
