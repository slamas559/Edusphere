from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.template.defaultfilters import slugify
from PIL import Image
from django.urls import reverse
import random


# Create your models here.
class Group(models.Model):
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by')
    members = models.ManyToManyField(User, related_name='members', blank=True)
    admin = models.ManyToManyField(User, related_name='admin', blank=True)
    date_created = models.DateTimeField(default=timezone.now)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(default="default.jpg", upload_to="group_pics", blank=True, null=True)
    slug = models.SlugField(default="", null=False, unique=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.id:
            self.id = random.randint(100000000000, 999999999999)  # 12-digit random number
        # if not self.slug:
        self.slug = f"{slugify(self.name)}-{self.id}"  # Example: 123456789012-my-title

        img = Image.open(self.profile_picture.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.profile_picture.path)

        self.admin.add(self.creator)
        self.members.add(self.creator)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("group-home")

class Question(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

class AnswerOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Wrong'})"

class MemberAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="membersanswer")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(AnswerOption, on_delete=models.CASCADE)
    correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'question']

    def is_correct(self):
        return self.selected_option.is_correct

class MemberScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'group')
        ordering = ['-points']

    def __str__(self):
        return f"{self.user.username} - {self.points} pts"
