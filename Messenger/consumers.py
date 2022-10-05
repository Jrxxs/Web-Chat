import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import User, Private_Log

connected_users = []


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        # print(self.scope)
        self.room_group_name = 'room_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # await self.send(text_data=json.dumps({
        #     'message': message
        # }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        client = text_data_json['author']
        companion = text_data_json['destination']
        date = text_data_json['date']

        Client = await self.get_user(username=client)
        Companion = await self.get_user(username=companion)

        await self.save_message(sender=Client, reciever=Companion, data=message, time=date)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'author': client,
                'date': date
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        client = event['author']
        date = event['date']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'author': client,
            'date': date
        }))

    @sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)

    @sync_to_async
    def save_message(self, sender, reciever, data, time):
        Private_Log.objects.create(From_User=sender, To_User=reciever, Message=data, Date_Time=time)



class Hub(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'hub_%s' % self.room_name

        connected_users.append(str(self.scope['user']))

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        await self.send(text_data=json.dumps({
            'message': 'init_connected_users_list',
            'connected_users': connected_users,
        }))

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'client_connected',
                'message': 'new_connectoin',
                'author': str(self.scope['user']),
            }
        )

    async def client_connected(self, event):
        message = event['message']
        client = event['author']
        # print(f"New connection")

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'author': client,
        }))

    async def disconnect(self, close_code):
        # Leave room group
        connected_users.remove(str(self.scope['user']))

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'client_disconnected',
                'message': 'disconnection',
                'author': str(self.scope['user']),
            }
        )

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def client_disconnected(self, event):
        message = event['message']
        client = event['author']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'author': client,
        }))

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        client = text_data_json['author']
        companion = text_data_json['destination']
        date = text_data_json['date']

        Client = await self.get_user(username=client)
        Companion = await self.get_user(username=companion)

        await self.save_message(sender=Client, reciever=Companion, data=message, time=date)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'author': client,
                'date': date
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        client = event['author']
        date = event['date']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'author': client,
            'date': date
        }))

    @sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)

    @sync_to_async
    def save_message(self, sender, reciever, data, time):
        Private_Log.objects.create(From_User=sender, To_User=reciever, Message=data, Date_Time=time)