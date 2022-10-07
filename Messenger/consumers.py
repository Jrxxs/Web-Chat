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
        data = json.loads(text_data)
        message = data['message']
        client = data['author']
        companion = data['destination']
        date = data['date']

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

    async def appearance_of_a_new_message(self, data):
        client = data['author']
        companion = data['destination']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_new_message_notification',
                'author': client,
                'destination': companion,
                'message': 'new_message'
            }
        )

    async def read_message(self, data):
        print("readed")

    commands = {
        'send_new_message': appearance_of_a_new_message,
        'read_message': read_message
    }

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)

        await self.commands[data['command']](self, data)

    # Receive message from room group
    async def user_new_message_notification(self, event):
        client = event['author']
        companion = event['destination']
        message = event['message']

        if companion == str(self.scope['user']):
            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'author': client,
                'message': message
            }))

    @sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)

    @sync_to_async
    def save_message(self, sender, reciever, data, time):
        Private_Log.objects.create(From_User=sender, To_User=reciever, Message=data, Date_Time=time)