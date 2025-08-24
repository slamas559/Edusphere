from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Group

@receiver(post_save, sender=Group)
def add_creator_to_admin(sender, instance, created, **kwargs):
    if created and instance.creator not in instance.admin.all():
        instance.admin.add(instance.creator)
        # Also add creator to members if not already
        if instance.creator not in instance.members.all():
            instance.members.add(instance.creator)
