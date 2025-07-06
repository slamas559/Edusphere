from django.contrib import admin
from .models import Message, GroupMessage

# Register your models here.
admin.site.register(Message)
admin.site.register(GroupMessage)
