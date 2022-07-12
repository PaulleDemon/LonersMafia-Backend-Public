from django.db import models
from django.conf import settings
from utils.customfields import ContentTypeRestrictedFileField
# Create your models here.


class Space(models.Model):
    """
        Each user can create their own space and start a chat. Looner is a char space for looners
    """

    name = models.CharField(max_length=30, null=False, unique=True)
    icon = ContentTypeRestrictedFileField(upload_to='space-icons/', content_types=['image/png', 'image/jpeg', 'image/gif'], 
                                            max_upload_size=5242880, null=True)
    about = models.CharField(max_length=250, null=True)

    created_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:

        verbose_name = 'space'
        verbose_name_plural = 'spaces'

    def __str__(self) -> str:
        return self.name


class Message(models.Model):

    space = models.ForeignKey(Space, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    message = models.TextField(max_length=2500, null=True)
    media = ContentTypeRestrictedFileField(upload_to='chat-media/', content_types=['image/png', 'image/jpeg', 'image/gif'], 
                                            max_upload_size=10485760, null=True)  # 20 mb max
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:

        verbose_name = 'message'
        verbose_name_plural = 'messages'
    
    def __str__(self):
        return self.message[:50]


class Reaction(models.Model):

    """
        reaction to certain message
    """

    class ReactionTypes(models.IntegerChoices):

        HEART = 0, 'heart'
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)

    reaction = models.PositiveSmallIntegerField(choices=ReactionTypes.choices)  

    def __str__(self):
        return f'{self.user.name} reacted with {self.reaction}'
