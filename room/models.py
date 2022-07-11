from datetime import datetime
from email import message
from django.db import models

from utils.customfields import ContentTypeRestrictedFileField
# Create your models here.

class Message(models.Model):

    message = models.TextField(max_length=2500, null=True)
    media = ContentTypeRestrictedFileField(upload_to='chat-media/', content_types=['image/png', 'image/jpeg', 'image/gif'], 
                                            max_upload_size=10485760, null=True)  # 20 mb max
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:

        verbose_name = 'message'
        verbose_name_plural = 'messages'