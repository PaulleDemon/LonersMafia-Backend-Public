from django.dispatch import receiver
from django.db.models.signals import post_save

from . import models

from mafia.models import Message


@receiver(post_save, sender=models.User)
def on_user_update(sender, instance, created, *args, **kwargs):

    print("saved: ", instance)

    if instance.avatar is None or not instance.avatar.storage.exists(instance.avatar.name): 
        # check if the avatar exists in the storage as well as db else set the default avatar
        instance.avatar.name = 'avatars/avatar-default.svg'
        instance.save()

