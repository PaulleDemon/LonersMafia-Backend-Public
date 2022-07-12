from django.dispatch import receiver
from django.db.models.signals import post_save

from . import models


@receiver(post_save)
def on_space_create(sender, instance, created, *args, **kwargs):

    """ 
        perform certain operations upon creation of the space
    """

    if created:
        # the creator of the space is assigned the moderator role in the beginning
        models.Moderator.objects.create(user=instance.created_by)
        