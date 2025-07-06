from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/comments/(?P<post_id>[^/]+)/$", consumers.CommentConsumer.as_asgi()),
]
