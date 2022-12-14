import json

from django.db.models import Q
from django.contrib.auth import get_user_model
#from django.contrib.auth.models import AnonymousUser

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


#from asgiref.sync import async_to_sync

# from django.dispatch import receiver
# from django.db.models.signals import post_save

from .models import Message, Mafia, BanUserFromMafia
from user.models import BlacklistedIp
# from .serializers import MessagesSerializer

User = get_user_model()


# The websocket unreserveed codes ranges from 3000 -4999, below is the definition of what the code means

# 3401 - user-banned from participating in the mafia
# 3404 - mafia not found

class ChatConsumer(AsyncWebsocketConsumer):
    """ This receives connection to chat creates room"""

    @database_sync_to_async
    def create_chat(self, msg, user):
        """ saves message to data base """

        if msg == "":
            return

        try:
            user = User.objects.get(id=user.id)

        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return

        try:
            mafia = Mafia.objects.get(name=self.room_name)
        
        except Mafia.DoesNotExist:
            return 

        Message.objects.create(mafia=mafia, user=user, message=msg)
        

    @database_sync_to_async
    def user_allowed(self):
        """ checks if the user isn't blacklisted """
        try:

            ip_address = self.scope['client'][0]
            black_listed = BlacklistedIp.objects.filter(Q(ip_address=ip_address) | Q(user=self.scope.get('user').id)).exists()
            banned_from_mafia = BanUserFromMafia.objects.filter(user=self.scope.get('user').id, mafia__name=self.room_name).exists()
            
            return (not black_listed and not banned_from_mafia)
        
        except (KeyError, IndexError, TypeError) as e:
            return False

    @database_sync_to_async
    def mafia_exists(self, mafia):
        """ checks if the mafia exists """

        return Mafia.objects.filter(name=mafia).exists()

    async def connect(self):

        """ Allows websocket connection """
        
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        await self.accept() # before closing we need to accept connection else the error code is always 1006

        if not await self.mafia_exists(self.room_name):
        
            await self.close(3404) # mafia not found
            # self.send(text_data="mafia doesn't exist", close=1008)
            return

        if not await self.user_allowed():
            await self.close(3401) # user not allowed
            return 

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
        """ 
            If text_data contains message it will be sent to save_message
            which will then save message in database. 
         """

        # print("Scope: ", self.scope)
        if not await self.user_allowed():
            await self.close(3401)
            return 

        if not await self.mafia_exists(self.room_name):
            await self.close(3404) # mafia not found
            # self.send(text_data="mafia doesn't exist", close=1008)
            return

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
        # ip_address = self.scope['client'][0]
        user = self.scope['user']

        if self.channel_name == event['sender_channel_name']:
            await self.create_chat(message, user)

    async def react_message(self, event):
        """ 
            reacts to message: 
            currently we don't use websockets to transmit reactions instead we use Http protocol
        """
        pass

    async def send_saved(self, event):
        """ sends the saved message from database. """

        await self.send(
            text_data=json.dumps(event['sender_data'])
        )

