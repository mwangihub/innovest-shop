import asyncio
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from django.urls import re_path

from shop.websocket_usecase import switch_message


class ShopMessagesConsumer1(AsyncWebsocketConsumer):
    async def connect(self):
        loop = asyncio.get_event_loop()
        await self.channel_layer.group_add('shop', self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard('shop', self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        await switch_message(data, self.scope)

    async def send_new_item(self, event=None):
        if event:
            data = event['text']
            await self.send(json.dumps(data))


class ShopMessagesConsumer(WebsocketConsumer):
    def connect(self):
        # self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        # self.room_group_name = "chat_%s" % self.room_name
        self.room_group_name = "shop"
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        """Receive message from WebSocket"""
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "send_new_item", "message": message}
        )

    def send_new_item(self, event):
        data = event["text"]
        self.send(text_data=json.dumps(data))


ws_urlpatterns = [
    re_path(r'ws/shop/messages/$', ShopMessagesConsumer.as_asgi())
]

'''
    # When implementing sockets in the views,
    # Decorate with 
    from channels.db import database_sync_to_async
    @database_sync_to_async
    # when interacting with DB
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)('shop_messages', {'type': 'send_shop_message', 'text': data_to_be_sent })
'''
