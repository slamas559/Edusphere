from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message, GroupMessage
from sections.groups.models import Group
from users.models import Profile
from django.db.models import Q
from django.contrib.auth import get_user_model
# Create your views here.

User = get_user_model()

@login_required
def chat_room(request, slug):
    """View for group chat rooms."""
    first_unread_id = None
    group = get_object_or_404(Group, slug=slug)
    messages = GroupMessage.objects.filter(room=group)
    messages = messages.order_by("timestamp")

    # Mark messages as read for this user only
    unread_messages = messages.exclude(read_by=request.user)
    for msg in unread_messages:
        msg.read_by.add(request.user)


    return render(request, "chat/chat_room.html", {"room": group, "chats": messages})

@login_required
def group_list(request):
    g_messages = GroupMessage.objects.filter()

    group_users = {}

    for message in g_messages:
        slug = message.room.slug # if message.receiver == request.user else message.receiver
        other_user = get_object_or_404(Group, slug=slug)

        # Store the last message and timestamp
        if request.user in other_user.members.all():
            if other_user not in group_users or group_users[other_user]['timestamp'] < message.timestamp:
                group_users[other_user] = {
                    'last_message': message.content,  # Store last message text
                    'sender': message.sender,
                    'timestamp': message.timestamp,  # Store last message time
                    'unread_count': GroupMessage.objects.filter(room=other_user).exclude(read_by=request.user).count(),  # Count of unread messages from the other user
                }

    # Sort users by last message timestamp (most recent first)
    group_chat_users = sorted(group_users.items(), key=lambda item: item[1]['timestamp'], reverse=True)

    context = {
        "group_users":group_chat_users,
    }

    return render(request, "chat/room_list.html", context = context)


@login_required
def chat_list(request):
    # Get all messages where the user is involved
    messages = Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user))

    # Dictionary to store last message details for each user
    chat_users = {}

    for message in messages:
        other_user = message.sender if message.receiver == request.user else message.receiver

        # Store the last message and timestamp
        if other_user not in chat_users or chat_users[other_user]['timestamp'] < message.timestamp:
            chat_users[other_user] = {
                'last_message': message.content,  # Store last message text
                'timestamp': message.timestamp,  # Store last message time
                'unread_count': Message.objects.filter(Q(sender=other_user, receiver=request.user, read=False)).count(),  # Count of unread messages from the other user
            }

    # Sort users by last message timestamp (most recent first)
    sorted_chat_users = sorted(chat_users.items(), key=lambda item: item[1]['timestamp'], reverse=True)

    
    context = {
        "chat_users":sorted_chat_users,
        }
    
    return render(request, "chat/chat_list.html", context = context)


@login_required
def private_chat(request, username):
    """View for private chat between two users."""
    receiver = get_object_or_404(User, username=username)
    # receiver = User.objects.get(username=username)
    messages = Message.objects.filter(sender=request.user, receiver=receiver) | \
               Message.objects.filter(sender=receiver, receiver=request.user)
    messages = messages.order_by("timestamp")
    # Mark messages as read for the current user
    unread_messages = Message.objects.filter(sender=receiver, receiver=request.user, read=False)
    unread_messages.update(read=True)
    return render(request, "chat/private_chat.html", {"receiver": receiver, "chats": messages})
