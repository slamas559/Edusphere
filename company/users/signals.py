from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        # Create a new profile only when the user is first created
        Profile.objects.create(user=instance)
    else:
        # Only update the profile if user fields are updated, not on login
        # Use update_fields to avoid unnecessary saves
        update_fields = kwargs.get('update_fields', None)
        if update_fields and not {'last_login'}.issuperset(update_fields):
            instance.profile.save()
