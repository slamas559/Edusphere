from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class AudioRoom(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_group = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')
    created_at = models.DateTimeField(default=timezone.now)
    allowed_users = models.ManyToManyField(User, related_name='audio_rooms', blank=True)  # for private access

    def __str__(self):
        return self.name

