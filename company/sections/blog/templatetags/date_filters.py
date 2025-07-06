from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def seconds(created_date):
    if created_date:
        time_since_creation = timezone.now() - created_date
    
        # Get total seconds from timedelta
        total_seconds = time_since_creation.total_seconds()
        return int(total_seconds)
    return 0
