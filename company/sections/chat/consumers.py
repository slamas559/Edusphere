import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model

# Use this to get the user model
User = get_user_model()


class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        from django.contrib.auth import get_user_model  # Lazy import
        User = get_user_model()

        self.user = self.scope["user"]
        self.receiver_username = self.scope["url_route"]["kwargs"]["receiver_username"]

        self.room_group_name = f"private_chat_{min(self.user.first_name, self.receiver_username)}_{max(self.user.first_name, self.receiver_username)}"
        self.chat_list_group = f"chat_list_{self.scope['user'].first_name}"

        await self.channel_layer.group_add(self.chat_list_group, self.channel_name)
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.chat_list_group, self.channel_name)

    async def receive(self, text_data):
        from django.contrib.auth import get_user_model
        from .models import Message
        User = get_user_model()

        data = json.loads(text_data)
        sender = self.user
        receiver = await sync_to_async(User.objects.get)(username=self.receiver_username)
        picture = await self.get_profile_picture_url(sender.first_name)
        total_count = await self.get_all_read_count(receiver)
        count = await self.get_read(receiver)

        message = await sync_to_async(Message.objects.create)(
            sender=sender,
            receiver=receiver,
            content=data["message"]
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": data["message"],
                "sender": sender.first_name,
                "timestamp": message.timestamp.strftime("%h:%M %p"),
                "unread_count": count,
            },
        )

        await self.channel_layer.group_send(
            "chat_list",
            {
                "type": "chat_list.update",
                "sender": sender.first_name,
                "receiver": receiver.first_name,
                "message": data["message"],
                "timestamp": message.timestamp.strftime('%H:%M %p'),
                "unread_count": count,
                "picture": picture,
                "chat_count": total_count,
            }
        )

    @sync_to_async
    def get_read(self, receiver):
        from .models import Message
        return Message.objects.filter(receiver=receiver, read=False).count()

    @sync_to_async
    def get_profile_picture_url(self, username):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(username=username)
        if user.profile.profile_picture and hasattr(user.profile.profile_picture, "url"):
            return user.profile.profile_picture.url
        return None

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def get_all_read_count(self, user):
        from .models import Message, GroupMessage
        private_count = Message.objects.filter(receiver=user, read=False).count()
        group_count = GroupMessage.objects.all().exclude(read_by=user).count()
        return private_count + group_count


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["slug"]
        self.room_group_name = f"chat_{self.room_name}"
        self.user = self.scope["user"]

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        from .models import GroupMessage
        data = json.loads(text_data)
        message = data["message"]

        user = self.user
        room = await self.get_group(self.room_name)
        new_message = await self.save_message(user, room, message)
        picture = await self.get_group_picture_url(self.room_name)
        user_picture = await self.get_profile_picture_url(user.first_name)
        total_count = await self.get_all_read_count(user)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": new_message["content"],
                "sender": new_message["sender"],
                "timestamp": new_message["timestamp"],
                "picture": user_picture,
            }
        )

        await self.channel_layer.group_send(
            f"group_chat_list",
            {
                "type": "group_list.update",
                "message": new_message["content"],
                "sender": new_message["sender"],
                "timestamp": new_message["timestamp"],
                "name": room.name,
                "slug": room.slug,
                "id": room.id,
                "picture": picture,
                "chat_count": total_count,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "timestamp": event["timestamp"],
            "picture": event["picture"],
        }))

    @sync_to_async
    def get_all_read_count(self, user):
        from .models import Message, GroupMessage
        private_count = Message.objects.filter(receiver=user, read=False).count()
        group_count = GroupMessage.objects.all().exclude(read_by=user).count()
        return private_count + group_count

    @sync_to_async
    def get_profile_picture_url(self, username):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(username=username)
        if user.profile.profile_picture and hasattr(user.profile.profile_picture, "url"):
            return user.profile.profile_picture.url
        return None

    @sync_to_async
    def get_group(self, room_name):
        from sections.groups.models import Group
        return Group.objects.get(slug=room_name)

    @sync_to_async
    def get_group_picture_url(self, room_name):
        from sections.groups.models import Group
        group = Group.objects.get(slug=room_name)
        return group.profile_picture.url

    @sync_to_async
    def save_message(self, user, room, content):
        from .models import GroupMessage
        message = GroupMessage.objects.create(sender=user, room=room, content=content)
        return {"sender": user.first_name, "content": message.content, "room": message.room, "timestamp": str(message.timestamp.strftime("%H:%M"))}


class ChatListConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.group_name = 'chat_list'
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def chat_list_update(self, event):
        await self.send(text_data=json.dumps({
            'sender': event['sender'],
            'receiver': event['receiver'],
            'message': event['message'],
            'timestamp': event['timestamp'],
            'unread_count': event['unread_count'],
            'picture': event['picture'],
            'chat_count': event['chat_count'],
        }))


class GroupListConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.group_name = f'group_chat_list'
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def group_list_update(self, event):
        room_slug = event["slug"]
        room = await self.get_group(room_slug)
        count = await self.get_read_count(room, self.user)

        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "timestamp": event["timestamp"],
            "id": event["id"],
            "slug": event["slug"],
            "name": event["name"],
            "picture": event["picture"],
            "unread_count": count,
            "chat_count": event['chat_count'],
        }))

    @sync_to_async
    def get_group(self, room_name):
        from sections.groups.models import Group
        return Group.objects.get(slug=room_name)

    @sync_to_async
    def get_read_count(self, room_name, user):
        from .models import GroupMessage
        return GroupMessage.objects.filter(room=room_name).exclude(read_by=user).count()
