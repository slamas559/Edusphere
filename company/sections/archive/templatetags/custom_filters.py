# custom_filters.py
from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    """Replaces all occurrences of the first part of arg with the second."""
    old, new = arg.split(',')
    return value.replace(old, new)
