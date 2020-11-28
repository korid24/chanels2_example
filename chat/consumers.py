import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


def simple_send(messege: str) -> str:
    return messege


def duplicate(messege: str) -> str:
    return f'{messege} ' * 2


def reverse_mes(messege: str) -> str:
    return messege[::-1]


actions = {
    'simple_send': simple_send,
    'duplicate': duplicate,
    'reverse_mes': reverse_mes
}


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']
        message = text_data_json['message']
        print(action)

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': actions[action](message),
                'action': action
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        action = event['action']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'action': action

        }))