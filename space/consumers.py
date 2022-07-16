import json

from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


from asgiref.sync import async_to_sync

# from django.dispatch import receiver
# from django.db.models.signals import post_save

from .models import Message,  Space, BanUserFromSpace
from user.models import BlacklistedIp
# from .serializers import MessagesSerializer

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    """ This receives connection to chat creates room"""

    @database_sync_to_async
    def create_chat(self, msg, sender_ip):
        """ saves message to data base """

        if msg == "":
            return

        try:
            user = User.objects.get(ip_address=sender_ip)

        except User.DoesNotExist:
            return

        try:
            space = Space.objects.get(name=self.room_name)
        
        except Space.DoesNotExist:
            return 

        Message.objects.create(space=space, user=user, message=msg)
        

    @database_sync_to_async
    def user_allowed(self):
        """ checks if the user isn't blacklisted """
        try:
            ip_address = self.scope['client'][0]
            black_listed = BlacklistedIp.objects.filter(ip_address=ip_address).exists()
            banned_from_space = BanUserFromSpace.objects.filter(ip_address=ip_address).exists()

            return (not black_listed and not banned_from_space)
        
        except (Exception):
            return False

    @database_sync_to_async
    def space_exists(self, space):
        """ checks if the space exists """

        return Space.objects.filter(name__iexact=space).exists()

    async def connect(self):

        """ Allows websocket connection """
        
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        await self.accept()

        if not await self.space_exists(self.room_name):
            print("Closed")
            await self.close(1008) # cannot use 1008 as close code must be between 3000-4999
            # self.send(text_data="Space doesn't exist", close=1008)
            # return

        if not await self.user_allowed():
            await self.close(1008)
            # return 

         # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )



    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        """ If text_data contains message it will be sent to save_message
         which will then save message in database. If it contains markread it will mark messages in 
         that room as read"""
        text_data_json = json.loads(text_data)
        
        message = None
        reaction = None

        if 'message' in text_data_json:
            message = text_data_json['message']

        if 'reaction' in text_data_json:
            reaction = text_data_json['reaction'] 

        # Send message to room group

        if message:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'save_message',
                    'message': message,
                    'sender_channel_name': self.channel_name
                }
            )

        elif reaction:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'react_message',
                    'room': reaction,
                    'sender_channel_name': self.channel_name
                }
            )

        # Receive message from room group
    async def save_message(self, event):
        """ calls the create chat and save the message to data base """

        message = event['message']

        # if isinstance(self.scope['user'], AnonymousUser):
        #     return 
        ip_address = self.scope['client'][0]

        if self.channel_name == event['sender_channel_name']:
            await self.create_chat(message, ip_address)

    async def react_message(self, event):
        """ calls the mark read to mark the messages as read """

        room = event['room']

        if self.channel_name != event['sender_channel_name']:
            await self.mark_message_read(room, self.scope['user'])

    async def send_saved(self, event):
        """ sends the saved message from database. """
        print("Sending message: ", event['sender_data'])
        await self.send(
            text_data=json.dumps(event['sender_data'])
        )

