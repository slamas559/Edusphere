import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from .models import Message, GroupMessage
from sections.groups.models import Group
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
        # await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_discard(self.chat_list_group, self.channel_name)


    async def receive(self, text_data):
        data = json.loads(text_data)
        sender = self.user
        receiver = await sync_to_async(User.objects.get)(username=self.receiver_username)
        picture = await self.get_profile_picture_url(sender.username)
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
                "sender": sender.username,
                "timestamp": message.timestamp.strftime("%H:%M %p"),
                "unread_count": count,
            },
        )

        await self.channel_layer.group_send(
            # f"chat_list_{receiver.username}",  # or sender.username depending on context
            "chat_list",  # or sender.username depending on context

            {
                "type": "chat_list.update",  # 🔥 matches chat_list_update
                "sender": sender.username,
                "receiver": receiver.username,
                "message": data["message"],
                "timestamp": message.timestamp.strftime('%H:%M %p'),
                "unread_count": count,  # must be calculated beforehand
                "picture": picture, #if hasattr(receiver, 'profile_picture') else None,
                "chat_count": total_count,
            }
        )

    @sync_to_async
    def get_read(self, receiver):
        return Message.objects.filter(receiver=receiver, read=False).count()
    
    @sync_to_async
    def get_profile_picture_url(self, username):
        user = User.objects.get(username=username)
        return user.profile.profile_picture.url

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def get_all_read_count(self, user):
        private_count = Message.objects.filter(receiver=user, read=False).count() # Count of unread messages from the other user
        group_count = GroupMessage.objects.all().exclude(read_by=user).count()
        total_count = private_count + group_count
        return total_count


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


        # user = await self.get_user(username)
        user  = self.user
        room = await self.get_group(self.room_name)
        new_message = await self.save_message(user, room, message)
        picture  = await self.get_group_picture_url(self.room_name)
        user_picture = await self.get_profile_picture_url(user.username)
        # count = await self.get_read_count(room, user) 
        total_count = await self.get_all_read_count(user)


        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": new_message["content"],
                "sender": new_message["sender"],
                "timestamp": new_message["timestamp"],
                "picture": user_picture
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
                # "unread_count": count,
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
        private_count = Message.objects.filter(receiver=user, read=False).count() # Count of unread messages from the other user
        group_count = GroupMessage.objects.all().exclude(read_by=user).count()
        total_count = private_count + group_count
        return total_count
    
    @sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)

    @sync_to_async
    def get_profile_picture_url(self, username):
        user = User.objects.get(username=username)
        return user.profile.profile_picture.url
    
    @sync_to_async
    def get_group(self, room_name):
        return Group.objects.get(slug=room_name)

    @sync_to_async
    def get_group_picture_url(self, room_name):
        group = Group.objects.get(slug=room_name)
        return group.profile_picture.url

    @sync_to_async
    def save_message(self, user, room, content):
        message = GroupMessage.objects.create(sender=user, room=room, content=content)
        return {"sender": user.username, "content": message.content, "room": message.room, "timestamp": str(message.timestamp.strftime("%H:%M, %b %d"))}

    @sync_to_async
    def get_previous_messages(self):
        messages = GroupMessage.objects.filter(room=self.room_name).order_by("-timestamp")[:20]
        return [{"sender": msg.sender, "content": msg.content, "timestamp": str(msg.timestamp)} for msg in messages]

class ChatListConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            # self.group_name = f'chat_list_{self.user.username}'
            self.group_name = 'chat_list'
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def chat_list_update(self, event):
        # This receives messages from group_send and forwards to WebSocket client
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
        return Group.objects.get(slug=room_name)

    @sync_to_async
    def get_read_count (self, room_name, user):
        return GroupMessage.objects.filter(room=room_name).exclude(read_by=user).count()