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
        client = data['sender']
        companion = data['receiver']
        date = data['date']

        Client = await self.get_user(username=client)
        Companion = await self.get_user(username=companion)

        Message_Id = await self.save_message(sender=Client, reciever=Companion, data=message, time=date)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': client,
                'date': date,
                'Message_Id': Message_Id
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        client = event['sender']
        date = event['date']
        Message_Id = event['Message_Id']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': client,
            'date': date,
            'Message_Id': Message_Id
        }))

    @sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)

    @sync_to_async
    def save_message(self, sender, reciever, data, time):
       obj = Private_Log.objects.create(From_User=sender, To_User=reciever, Message=data, Date_Time=time)
       return obj.id


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
                'sender': str(self.scope['user']),
            }
        )

    async def client_connected(self, event):
        message = event['message']
        client = event['sender']
        # print(f"New connection")

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': client,
        }))

    async def disconnect(self, close_code):
        # Leave room group
        connected_users.remove(str(self.scope['user']))

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'client_disconnected',
                'message': 'disconnection',
                'sender': str(self.scope['user']),
            }
        )

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def client_disconnected(self, event):
        message = event['message']
        client = event['sender']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': client,
        }))

    async def appearance_of_a_new_message(self, data):
        client = data['sender']
        companion = data['receiver']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_new_message_notification',
                'message': 'new_message',
                'sender': client,
                'receiver': companion
            }
        )

    async def read_message(self, data):
        Id = data['id']

        if (await self.set_readed_status(int(Id))):
            await self.send(text_data=json.dumps({
                    'message': 'reading_error'
                }))
        else:
            await self.send(text_data=json.dumps({
                    'message': 'reading_successful',
                    'sender': data['sender'],
                    'id': Id
                }))

    async def find_persons(self, data):

        users = await self.get_user_list(data['query'])

        if users == 0:
            users = 'no_users'
        
        await self.send(text_data=json.dumps({
                'message': 'finded',
                'users': users
            }))

    async def refresh_conn_users(self, data):

        await self.send(text_data=json.dumps({
            'message': 'init_connected_users_list',
            'connected_users': connected_users,
        }))


    commands = {
        'send_new_message': appearance_of_a_new_message,
        'read_message': read_message,
        'find_persons': find_persons,
        'refresh_conn_users' : refresh_conn_users
    }

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)

        await self.commands[data['command']](self, data)

    # Receive message from room group
    async def user_new_message_notification(self, event):
        client = event['sender']
        companion = event['receiver']
        message = event['message']

        if companion == str(self.scope['user']):
            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'sender': client,
                'message': message,
                # 'id': ,
            }))

    @sync_to_async
    def get_user_list(self, username):
        UserList = User.objects.filter(username__contains=username, is_superuser=False).values()
        if UserList:
            return json.dumps([{'id': User.objects.get(id=u['id']).users.id, 'username': u['username'], 'Photo': User.objects.get(id=u['id']).users.get_photo_url(), \
                'Status': 'Online' if u['username'] in connected_users else 'Offline'} for u in UserList])
        else:
            return 0
    
    @sync_to_async
    def set_readed_status(self, id):
        try:
            Private_Log.objects.filter(id=id).update(Status=True)
        except:
            return 1
        return 0