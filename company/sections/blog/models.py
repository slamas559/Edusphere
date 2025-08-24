from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
import uuid
import random
# from django.utils.text import slugify
from django.template.defaultfilters import slugify
from PIL import Image
from sections.notifications.views import send_notification


# Create your models here.

class Post(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author =  models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="post_images/", blank=True, null=True)
    slug = models.SlugField(default="", null=False, unique=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)

    def total_likes(self):
        return self.likes.count()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = random.randint(100000000000, 999999999999)  # 12-digit random number
        if not self.slug:
            self.slug = f"{self.id}-{slugify(self.title)}"  # Example: 123456789012-my-title
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def top_level_comments(self):
        return self.comment.filter(parent__isnull=True)


    def get_absolute_url(self):
        return reverse("blog-home")
    # , kwargs={"pk":self.pk}


class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user.first_name} on {self.post.title}"

    def is_parent(self):
        return self.parent is None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        send_notification(self.post.author, self.user, f"{self.user.first_name} commented on your post '{self.post.title}'", "comment")

