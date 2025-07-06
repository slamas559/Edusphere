# your_app/templatetags/contains_user.py
from django import template

register = template.Library()

@register.filter
def contains_user(user_list, user):
    return user in user_list
