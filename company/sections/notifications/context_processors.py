from .models import Notification
from django.contrib.auth.decorators import login_required

# @login_required
def notification_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {"notification_count": count}
    return {"notification_count": 0}