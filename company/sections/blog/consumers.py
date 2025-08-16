from channels.generic.websocket import AsyncWebsocketConsumer
from django.template.loader import render_to_string
from django.utils import timezone
from asgiref.sync import sync_to_async
import json


class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.post_id = self.scope["url_route"]["kwargs"]["post_id"]
        self.room_group_name = f"comments_{self.post_id}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data["content"]
        parent_id = data.get("parent_id")
        user = self.scope["user"]

        if not user.is_authenticated:
            return

        post = await self.get_post(self.post_id)
        comment = await self.create_comment(user, post, content, parent_id)

        # ✅ render comment in sync-safe way
        rendered = await self.render_comment_html(comment)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "send_comment",
                "comment_html": rendered,
                "parent_id": parent_id,
            }
        )

    async def send_comment(self, event):
        await self.send(text_data=json.dumps({
            "comment_html": event["comment_html"],
            "parent_id": event["parent_id"],
        }))

    @sync_to_async
    def get_post(self, post_id):
        from .models import Post   # ✅ lazy import
        return Post.objects.get(id=post_id)

    @sync_to_async
    def create_comment(self, user, post, content, parent_id):
        from .models import Comment   # ✅ lazy import
        return Comment.objects.create(
            user=user,
            post=post,
            content=content,
            created_at=timezone.now(),
            parent_id=parent_id if parent_id else None
        )

    @sync_to_async
    def render_comment_html(self, comment):       
        return render_to_string("blog/partials/comment.html", {"comment": comment})
