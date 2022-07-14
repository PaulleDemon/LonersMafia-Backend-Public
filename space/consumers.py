from ipaddress import ip_address
import json

from django.db.models import Q
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import async_to_sync

# from asgiref.sync import async_to_sync
# from django.dispatch import receiver
# from django.db.models.signals import post_save

from .models import Message,  Space, BanUserFromSpace
from user.models import BlacklistedIp
# from .serializers import MessagesSerializer

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    """ This receives connection to chat creates room"""

    # @database_sync_to_async
    # def create_space(self, msg, sender):
    #     """ saves message to data base """
  
    #     if msg == "":
    #         return

    #     try:
    #         room = Room.objects.get(id=self.room_name)
        
    #     except Room.DoesNotExist:
    #         return 

    #     recipient = room.user2 if sender != room.user2 else room.user1 
    #     Message.objects.create(room=room, sender=sender, recipient=recipient, message=msg)
        

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

    async def connect(self):
        print("Test: ", self.scope['client'][0])
        
        self.space_name = self.scope['url_route']['kwargs']['room_name']
        self.space_group_name = 'chat_%s' % self.space_name

        if not self.user_allowed():
            return 

        # Join room group
        await self.channel_layer.group_add(
            self.space_group_name,
            self.channel_name
        )


        await self.accept()


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
        room = None

        if 'message' in text_data_json:
            message = text_data_json['message']

        if 'markread' in text_data_json:
            room = text_data_json['markread'] 

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

        elif room:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'mark_read',
                    'room': room,
                    'sender_channel_name': self.channel_name
                }
            )

        # Receive message from room group
    async def save_message(self, event):
        """ calls the create chat and save the message to data base """
        message = event['message']

        if self.channel_name == event['sender_channel_name']:
            await self.create_chat(message, self.scope['user'])

    async def mark_read(self, event):
        """ calls the mark read to mark the messages as read """

        room = event['room']

        if self.channel_name != event['sender_channel_name']:
            await self.mark_message_read(room, self.scope['user'])

    async def send_saved(self, event):
        """ sends the saved message from database. """

        await self.send(
            text_data=json.dumps(event['sender_data'])
        )

