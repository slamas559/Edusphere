from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.template.defaultfilters import slugify
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# Create your models here.
class CustomUserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

LEVELS = [
    ('secondary', 'Secondary'),
    ('undergraduate', 'Undergraduate'),
    ('tertiary', 'Tertiary Instituition'),
    ('postgraduate', 'Postgraduate')
]

class Profile(models.Model):
    # Change from User to CustomUser
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    school = models.CharField(max_length=250, default="")
    education_level = models.CharField(choices=LEVELS, default="", max_length=250)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    cover_photo = models.ImageField(upload_to="cover_photos/", blank=True, null=True)
    slug = models.SlugField(default="", null=False, unique=True)

    def __str__(self):
        return f"{self.user.email} Profile"

    def save(self, *args, **kwargs):
        if not self.slug:
            # Use email instead of username for slug
            base_slug = slugify(f"{self.user.email.split('@')[0]}")
            self.slug = base_slug
            counter = 1
            while Profile.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        
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