from datetime import datetime
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models.functions import Lower
from django.db.models import UniqueConstraint
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

from rest_framework import status

from utils.customfields import ContentTypeRestrictedFileField
# Create your models here.

mafia_name_validator = RegexValidator(regex='^[a-zA-Z][a-zA-Z0-9_-]+$', message='can contain only alpha numeric and -, _ and must begin with alphabet', code=status.HTTP_400_BAD_REQUEST)
color_validator = RegexValidator(regex='^#(?:[0-9a-fA-F]{3,4}){1,2}$', message='not a valid hex color code', code=status.HTTP_400_BAD_REQUEST)


class Mafia(models.Model):
    """
        Each user can create their own mafia and start a chat. Loner is a chat mafia for loners
    """
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=False)

    name = models.CharField(max_length=30, null=False, unique=True, validators=[mafia_name_validator])
    verbose_name = models.CharField(max_length=40, null=True, blank=True) # this is a verbose name (invite to join memers)

    icon = ContentTypeRestrictedFileField(upload_to='mafia-dashboards/', content_types=['image/png', 'image/jpeg', 'image/gif', 'image/svg+xml'], 
                                            max_upload_size=5242880, null=True, blank=True, default='mafia-dashboards/loner-icon.svg')
    about = models.CharField(max_length=350, null=True, blank=True)
    tag_line = models.CharField(max_length=75, default="", null=True, blank=True)

    color_theme = models.CharField(max_length=16, validators=[color_validator], default="#00FFFFFF", null=False, blank=False) 
    background_image = ContentTypeRestrictedFileField(upload_to='mafia_background/', content_types=['image/png', 'image/jpeg', 'image/gif', 'image/svg+xml'],
                                                        max_upload_size=5242880, null=True, blank=True)

    created_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:

        verbose_name = 'mafia'
        verbose_name_plural = 'mafias'

        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='name_unique',
            ),
        ]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:

        # if mafia.objects.filter(name__iexact=self.name).exists():
        #     raise ValidationError(message='This mafia already exists.', code=status.HTTP_400_BAD_REQUEST)

        return super().clean()


class Rule(models.Model):

    """
        The user who create the mafia can enfoce certain rules
    """

    mafia = models.ForeignKey(Mafia, on_delete=models.CASCADE)
    rule = models.CharField(max_length=100)

    class Meta:

        verbose_name = 'mafia rule'
        verbose_name_plural = 'mafia rules'

    def __str__(self) -> str:
        return self.rule


class Moderator(models.Model):

    """
        Moderators are privileged users that can delete other's messages and ban users from a mafia
    """

    mafia = models.ForeignKey(Mafia, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True) # date time when the user was made moderator of that mafia

    def __str__(self):
        return f'{self.user.name} is a mod of {self.mafia.name}'


class Message(models.Model):

    mafia = models.ForeignKey(Mafia, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    message = models.TextField(max_length=2500, null=True)
    media = ContentTypeRestrictedFileField(upload_to='chat-media/', content_types=['image/png', 'image/jpeg', 'image/gif', 'image/svg'], 
                                            max_upload_size=10485760, null=True, blank=True)  # 20 mb max
    
    datetime = models.DateTimeField(default=timezone.now) #auto_now_add=True

    class Meta:

        verbose_name = 'message'
        verbose_name_plural = 'messages'
    
    def __str__(self):
        return self.message[:50] if self.message else ''


class Reaction(models.Model):

    """
        reaction to certain message
    """ 

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=10, null=False, blank=False)

    def __str__(self):
        return f'{self.user.name} reacted with {self.reaction}'

    
    def clean(self) -> None:

        allowed_reactions = ['🚀', '😭', '🤣', '👎']

        if self.reaction not in allowed_reactions:
            raise ValidationError(message=f'This reaction is not allowed yet, allowed reactions are {",".join(allowed_reactions)}')

        if Reaction.objects.filter(user=self.user, message=self.message, reaction=self.reaction).exists():
            raise ValidationError(message='User has already reacted with this emoji', code=status.HTTP_400_BAD_REQUEST)

        return super().clean()


class BanUserFromSpace(models.Model):

    """
        This bans user from participating in a mafia
    """

    mafia = models.ForeignKey(Mafia, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)