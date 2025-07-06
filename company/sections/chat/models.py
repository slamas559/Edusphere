from django.db import models
from django.contrib.auth.models import User
from sections.groups.models import Group

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages", null=True, blank=True)
    content = models.TextField()
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        if self.receiver:
            return f"Private: {self.sender.username} → {self.receiver.username}: {self.content[:20]}"
        return f"Group: {self.sender.username}: {self.content[:20]}"

class GroupMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_messages")
    room = models.ForeignKey(Group, on_delete=models.CASCADE, default="")
    content = models.TextField()
    read_by = models.ManyToManyField(User, related_name="group_messages_read", blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"Group: {self.sender.username}: {self.content[:20]}"
