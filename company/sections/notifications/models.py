from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from sections.groups.models import Group

# Create your models here.
# notifications/models.py

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('alert', 'Alert'),
        ('invite', 'Invite'),
        {'request', 'Request'},
        ('reminder', 'Reminder'),
        ('update', 'Update'),
        ('warning', 'Warning'),
        ('info', 'Info'),
        ('error', 'Error'),
        ('success', 'Success'),
        ('message', 'Message'),
        ('like', 'Like'),
        ('comment', 'Comment'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, default="", on_delete=models.CASCADE, related_name='sent_notifications')
    message = models.TextField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='groups', blank=True, null=True, default="")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='alert')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} - {self.notification_type}"
