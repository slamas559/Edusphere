from django.contrib import admin
from .models import Group, Question, AnswerOption, MemberScore, MemberAnswer, Post, Comment
# Register your models here.

admin.site.register(Group)
admin.site.register(Question)
admin.site.register(AnswerOption)
admin.site.register(MemberScore)
admin.site.register(MemberAnswer)
admin.site.register(Post)
admin.site.register(Comment)
