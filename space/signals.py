from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.db.models import Count
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete


from . import models
from .serializers import MessageSerializer


@receiver(post_save, sender=models.Mafia)
def on_mafia_create(sender, instance, created, *args, **kwargs):

    """ 
        perform certain operations upon creation of the mafia
    """

    if created:
        # the creator of the mafia is assigned the moderator role in the beginning
        models.Moderator.objects.create(user=instance.created_by, mafia=instance)


@receiver(post_delete, sender=models.Moderator)
def on_mod_delete(sender, instance, *args, **kwargs):

    """
        if no moderator exists then assaign a mod to some else who frequently sends messages in that mafia
    """
    
    if not models.Moderator.objects.filter(mafia=instance.mafia).exists(): 
        msg = models.Message.objects.filter(mafia=instance.mafia).annotate(freq_messages=Count('user')).order_by('-freq_messages', '-datetime')

        if msg.exists():

            user = msg.first()
            if user:
                models.Moderator.objects.create(user=user.user, mafia=instance.mafia)


@receiver(post_save, sender=models.Message)
def handle_message(sender, instance, created, *args, **kwargs):
    """
        Deletes the message if the sender_deleted and recipient_deleted is set to True.
        Once the message is saved using consumers. It sends the message through the websocket connection.
    """
    
    if created:
        
        channel_layer = get_channel_layer()
        
        sender_serializer = MessageSerializer(instance, context={'user': instance.user.id})

        async_to_sync(channel_layer.group_send)(
            f'chat_{instance.mafia.name}',
            {'type': 'send_saved', 
             'sender_data': sender_serializer.data, 
            }
        )


@receiver(post_delete, sender=models.Message)
def handle_delete_message(sender, instance, *args, **kwargs):

    channel_layer = get_channel_layer()
        
    sender_serializer = MessageSerializer(instance, context={'user': instance.user.id})

    async_to_sync(channel_layer.group_send)(
        f'chat_{instance.mafia.name}',
        {'type': 'send_saved', 
            'sender_data': {'delete': instance.id}, 
        }
    )