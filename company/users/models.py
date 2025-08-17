from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
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
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    slug = models.SlugField(default="", null=False, unique=True)


    def __str__(self):
        return f"{self.user.username} Profile"

    def save(self, *args, **kwargs):
        # Only process if profile_picture is a new upload (not an existing remote Cloudinary file)
        if self.profile_picture and hasattr(self.profile_picture, "_file"):  
            try:
                img = Image.open(self.profile_picture)

                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)

                    buffer = BytesIO()
                    img.save(buffer, format="JPEG")

                    self.profile_picture.save(
                        self.profile_picture.name,
                        ContentFile(buffer.getvalue()),
                        save=False,
                    )
            except Exception as e:
                import logging
                logging.warning(f"Profile picture processing failed: {e}")

        super().save(*args, **kwargs)

