from datetime import datetime
from django.db import models
from django.utils import timezone
# Create your models here.

class Privacy(models.Modal):

    privacy = models.TextField()
    datetime = models.DateTimeField(default=timezone.now) # you can also add auto_now=True


class TermsAndConditions(models.Modal):

    terms_and_conditions = models.TextField()
    datetime = models.DateTimeField(default=timezone.now)