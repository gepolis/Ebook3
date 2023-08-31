import json
import re

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from Accounts.models import Account
from PersonalArea.models import Message


# class ChatCostumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.classroom = self.scope['url_route']['kwargs']['classroom']
#         self.classroom_group_name = 'chat_%s' % self.classroom
#         print(self.)
#         await self.channel_layer.group_add(
#             str(self.classroom),
#             self.channel_name
#         )
#
#         await self.accept()
#
#     async def disconnect(self, code):
#         await self.channel_layer.group_discard(
#             str(self.classroom),
#             self.channel_name
#         )
#
#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         print(data)
#         message =data['message']
#         username =data['username']
#         classroom = data['classroom']
#
#         await self.channel_layer.group_send(
#             self.classroom_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message,
#                 'username': username,
#                 'room': classroom
#             }
#         )
#
#     async def chat_message(self, event):
#         print(event)
#         message = event['message']
#         username = event['username']
#         room = event['room']
#
#         t = await self.send(text_data=json.dumps({
#             'message': message,
#             'username': username,
#             'room': room
#         }))
#         print(t)
#

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        #if self.scope['user'].is_anonymous:
        #    await self.close()

        self.room_name = self.scope['url_route']['kwargs']['classroom']
        self.room_group_name = 'chat_%s' % self.room_name
        print("connect")

        # Присоединяемся к группе комнаты
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Покидаем группу комнаты
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Получение сообщения от клиента
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        message = re.sub("<.*?>", "", message)
        username = text_data_json['username']
        author = text_data_json['author']
        room = text_data_json['room']
        avatar = text_data_json['avatar']
        await self.save_message(author, message, room)
        # Отправка сообщения всем клиентам в группе комнаты
        if message != "":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'username': username,
                    'message': message,
                    'author': author,
                    'avatar': avatar
                }
            )

    # Отправка сообщения клиенту
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        author = event['author']
        avatar = event['avatar']
        # Отправка сообщения клиенту
        await self.send(text_data=json.dumps({
            'username': username,
            'message': message,
            'author': author,
            'avatar': avatar
        }))

    @sync_to_async
    def save_message(self, author, content, room):
        user = Account.objects.get(pk=author)
        Message.objects.create(user=user, room=room, context=content).save()
