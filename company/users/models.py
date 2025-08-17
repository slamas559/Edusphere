from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from PIL import Image
from django.urls import reverse

# Create your models here.
LEVELS = [
        ('secondary', 'Secondary'),
        ('undergraduate', 'Undergraduate'),
        ('tertiary', 'Tertiary Instituition'),
        ('postgraduate', 'Postgraduate')
    ]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    school = models.CharField(max_length=250, default="")
    education_level = models.CharField(choices=LEVELS, default="", max_length=250)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(default="default.jpg", upload_to="profile_pics/", blank=True, null=True)
    slug = models.SlugField(default="", null=False, unique=True)


    def __str__(self):
        return f"{self.user.username} Profile"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.profile_picture.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.profile_picture.path)
         
        if not self.slug:
            self.slug = f"{self.user.id}-{slugify(self.user.username)}"  # Example: 123456789012-my-title

# for profile in Profile.objects.all():
#     profile.slug = f"{profile.user.id}-{slugify(profile.user.username)}"
#     profile.save()
