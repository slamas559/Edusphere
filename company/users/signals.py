# users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile

# Use settings.AUTH_USER_MODEL to work with your custom user model
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        # Create a new profile only when the user is first created
        Profile.objects.create(user=instance)
        print(f"Created profile for {instance.email}")  # Debugging
    else:
        # Only update the profile if user fields are updated, not on login
        update_fields = kwargs.get('update_fields', None)
        if update_fields and not {'last_login'}.issuperset(update_fields):
            # Use try/except to handle cases where profile doesn't exist
            try:
                instance.profile.save()
            except Profile.DoesNotExist:
                Profile.objects.create(user=instance)