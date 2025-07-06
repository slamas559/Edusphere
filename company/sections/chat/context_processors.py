from .models import Message, GroupMessage
from sections.groups.models import Group
from django.contrib.auth.decorators import login_required

# @login_required
def message_count(request):
    if request.user.is_authenticated:
        groups = Group.objects.filter(members=request.user)
        private_count = Message.objects.filter(receiver=request.user, read=False).count() # Count of unread messages from the other user
        group_count = GroupMessage.objects.filter(room__in=groups).exclude(read_by=request.user).count()
        total_count = private_count + group_count
        return {"message_count": total_count}
    return {"message_count": 0}

