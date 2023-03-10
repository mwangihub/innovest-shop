import json

from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer

from django.urls import path, re_path

from shop.websocket_usecase import switch_message

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


class ShopMessagesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add('shop', self.channel_name)
        await self.accept()
        # await self.send(text_data={'connected':"connected from backend"}, bytes_data=None, close=False)

    async def disconnect(self, code):
        await self.channel_layer.group_discard('shop', self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        await switch_message(data, self.scope)

    async def send_new_item(self, event=None):
        if event:
            data = event['text']
            await self.send(json.dumps(data))


ws_urlpatterns = [
    re_path(r'ws/shop/messages/$', ShopMessagesConsumer.as_asgi())
]
