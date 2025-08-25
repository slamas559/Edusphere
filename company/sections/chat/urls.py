from django.urls import path
from .views import chat_room, private_chat, chat_list, group_list

urlpatterns = [
    path("room/<slug:slug>/", chat_room, name="chat-room"),
    path("chatlist/", chat_list, name="chat-list"),
    path("grouplist/", group_list, name="group-list"),
    path("private/<int:id>/", private_chat, name="private-chat"),
]
