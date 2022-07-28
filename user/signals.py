from django.dispatch import receiver
from django.db.models.signals import post_save

from . import models

from mafia.models import Message

        