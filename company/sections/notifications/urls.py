# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox, name='notification-inbox'),
    path('read/<int:pk>/', views.read_notification, name='mark-notification-as-read'),
]
