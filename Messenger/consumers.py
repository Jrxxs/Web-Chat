import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import User, Private_Log

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        client = text_data_json['author']
        companion = text_data_json['destination']
        date = text_data_json['date']
        Client = User.objects.get(username=client)
        Companion = User.objects.get(username=companion)
        Private_Log.objects.create(From_User=Client, To_User=Companion, Message=message, Date_Time=date)

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'author': client,
                'date': date
            }
        )

    def chat_message(self, event):
        message = event['message']
        client = event['author']
        date = event['date']

        async_to_sync(self.send(text_data=json.dumps({
            'message': message,
            'author': client,
            'date': date
        })))
