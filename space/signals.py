from django.db.models import Count
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from . import models


@receiver(post_save, sender=models.Space)
def on_space_create(sender, instance, created, *args, **kwargs):

    """ 
        perform certain operations upon creation of the space
    """

    if created:
        # the creator of the space is assigned the moderator role in the beginning
        models.Moderator.objects.create(user=instance.created_by, space=instance)


@receiver(post_delete, sender=models.Moderator)
def on_mod_delete(sender, instance, *args, **kwargs):

    """
        if no moderator exists then assaign a mod to some else who frequently sends messages in that space
    """
    
    if not models.Moderator.objects.filter(space=instance.space).exists(): 
        msg = models.Message.objects.filter(space=instance.space).annotate(freq_messages=Count('user')).order_by('-freq_messages', '-datetime')

        user = msg.first()
        if user:
            models.Moderator.objects.create(user=user.user)
