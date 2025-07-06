from django.urls import path
from . import views

urlpatterns = [
    path('room/<str:room_name>/', views.group_room_view, name='group-audio-room'),
    path('room/invite/<str:room_name>/', views.join_room, name='audio-room-invite'),
    path('create/', views.create_room, name='create-audio-room'),
]
