from django.shortcuts import render
from .models import Notification
from django.contrib.auth.decorators import login_required
from asgiref.sync import async_to_sync
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
import json
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model

# Use this to get the user model
User = get_user_model()


# Create your views here.
# views.py


@login_required
def inbox(request):
    notifications = request.user.notifications.order_by('-created_at')
    return render(request, 'notifications/inbox.html', {'notifications': notifications})

@login_required
def read_notification(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    # Redirect to the desired location, or back to inbox
    return redirect('notification-inbox')


def send_notification(user, sender, message, notification_type, group=None):
    notif = Notification.objects.create(user=user, sender=sender, message=message, group=group, notification_type=notification_type)
    count = Notification.objects.filter(user=user, is_read=False).count()

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'notifications_{user.id}',
        {
            'type': 'send.notification',
            'sender': notif.sender.first_name,
            'receiver': user.id,
            'message': notif.message,
            'notify_type': notif.notification_type,
            'created_at': notif.created_at.strftime("%Y-%m-%d %H:%M"),
            'count': count
        }   
    )

    
