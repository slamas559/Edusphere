from django.contrib import admin
from .models import Group, Question, AnswerOption, MemberScore, MemberAnswer
# Register your models here.

admin.site.register(Group)
admin.site.register(Question)
admin.site.register(AnswerOption)
admin.site.register(MemberScore)
admin.site.register(MemberAnswer)
