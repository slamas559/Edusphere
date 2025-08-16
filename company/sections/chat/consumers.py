import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.apps import apps
from asgiref.sync import sync_to_async

User = get_user_model()


class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.receiver_username = self.scope["url_route"]["kwargs"]["receiver_username"]
        self.room_group_name = f"private_chat_{min(self.user.username, self.receiver_username)}_{max(self.user.username, self.receiver_username)}"
        self.chat_list_group = f"chat_list_{self.scope['user'].username}"

        await self.channel_layer.group_add(self.chat_list_group, self.channel_name)
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.chat_list_group, self.channel_name)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        sender = self.user
        receiver = await sync_to_async(User.objects.get)(username=self.receiver_username)

        Message = apps.get_model("chat", "Message")
        GroupMessage = apps.get_model("chat", "GroupMessage")

        picture = await self.get_profile_picture_url(sender.username)
        total_count = await self.get_all_read_count(receiver, Message, GroupMessage)
        count = await self.get_read(receiver, Message)

        message = await sync_to_async(Message.objects.create)(
            sender=sender, receiver=receiver, content=data["message"]
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": data["message"],
                "sender": sender.username,
                "timestamp": message.timestamp.strftime("%H:%M %p"),
                "unread_count": count,
            },
        )

        await self.channel_layer.group_send(
            "chat_list",
            {
                "type": "chat_list.update",
                "sender": sender.username,
                "receiver": receiver.username,
                "message": data["message"],
                "timestamp": message.timestamp.strftime("%H:%M %p"),
                "unread_count": count,
                "picture": picture,
                "chat_count": total_count,
            },
        )

    @sync_to_async
    def get_read(self, receiver, Message):
        return Message.objects.filter(receiver=receiver, read=False).count()

    @sync_to_async
    def get_profile_picture_url(self, username):
        user = User.objects.get(username=username)
        return user.profile.profile_picture.url if user.profile.profile_picture else None

    @sync_to_async
    def get_all_read_count(self, user, Message, GroupMessage):
        private_count = Message.objects.filter(receiver=user, read=False).count()
        group_count = GroupMessage.objects.exclude(read_by=user).count()
        return private_count + group_count

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))


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
        data = json.loads(text_data)
        message = data["message"]

        Group = apps.get_model("groups", "Group")
        Message = apps.get_model("chat", "Message")
        GroupMessage = apps.get_model("chat", "GroupMessage")

        user = self.user
        room = await self.get_group(self.room_name, Group)
        new_message = await self.save_message(user, room, message, GroupMessage)
        picture = await self.get_group_picture_url(self.room_name, Group)
        user_picture = await self.get_profile_picture_url(user.username)
        total_count = await self.get_all_read_count(user, Message, GroupMessage)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": new_message["content"],
                "sender": new_message["sender"],
                "timestamp": new_message["timestamp"],
                "picture": user_picture,
            },
        )

        await self.channel_layer.group_send(
            "group_chat_list",
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
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def get_all_read_count(self, user, Message, GroupMessage):
        private_count = Message.objects.filter(receiver=user, read=False).count()
        group_count = GroupMessage.objects.exclude(read_by=user).count()
        return private_count + group_count

    @sync_to_async
    def get_profile_picture_url(self, username):
        user = User.objects.get(username=username)
        return user.profile.profile_picture.url if user.profile.profile_picture else None

    @sync_to_async
    def get_group(self, room_name, Group):
        return Group.objects.get(slug=room_name)

    @sync_to_async
    def get_group_picture_url(self, room_name, Group):
        group = Group.objects.get(slug=room_name)
        return group.profile_picture.url if group.profile_picture else None

    @sync_to_async
    def save_message(self, user, room, content, GroupMessage):
        message = GroupMessage.objects.create(sender=user, room=room, content=content)
        return {
            "sender": user.username,
            "content": message.content,
            "timestamp": message.timestamp.strftime("%H:%M, %b %d"),
        }


class ChatListConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            self.group_name = "chat_list"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def chat_list_update(self, event):
        await self.send(text_data=json.dumps(event))


class GroupListConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            self.group_name = "group_chat_list"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def group_list_update(self, event):
        Group = apps.get_model("groups", "Group")
        GroupMessage = apps.get_model("chat", "GroupMessage")

        room_slug = event["slug"]
        room = await self.get_group(room_slug, Group)
        count = await self.get_read_count(room, self.user, GroupMessage)

        await self.send(text_data=json.dumps({
            **event,
            "unread_count": count,
        }))

    @sync_to_async
    def get_group(self, room_name, Group):
        return Group.objects.get(slug=room_name)

    @sync_to_async
    def get_read_count(self, room, user, GroupMessage):
        return GroupMessage.objects.filter(room=room).exclude(read_by=user).count()
