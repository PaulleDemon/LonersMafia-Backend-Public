from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from rest_framework import status

from utils.customfields import ContentTypeRestrictedFileField


# custom manager
class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where username is the unique identifier.
    """
    def create_user(self, username, password, ip_address=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """

        if not username:
            raise ValueError('The user name must be set')
       
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password. (email only for superusers)
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        if not email:
            raise ValueError('The Email must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        return user


user_name_validator = RegexValidator(regex='^[a-zA-Z][a-zA-Z0-9_-]+$', message='can contain only alpha numeric and -, _ and must begin with alphabet', code=status.HTTP_400_BAD_REQUEST)


class User(AbstractBaseUser, PermissionsMixin):

    name = models.CharField(unique=True, null=True, blank=False, max_length=30, validators=[user_name_validator])
    avatar = ContentTypeRestrictedFileField(upload_to='avatars/', content_types=['image/png', 'image/jpeg', 'image/svg+xml'], 
            max_upload_size=10485760, default='avatars/avatar-default.svg', null=True)  # 20 mb max

    ip_address = models.GenericIPAddressField(null=True, blank=True) # the ip is stored to prevent attacks on server
    email = models.EmailField(unique=True, null=True, blank=True) # used only for staff/admin users

    tag_line = models.CharField(max_length=75, null=True, blank=True)

    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    date_joined = models.DateTimeField(default=timezone.now) # you can also use auto_add_now=True

    objects = CustomUserManager()

    USERNAME_FIELD = 'email' # emails only for admins and staffs
    REQUIRED_FIELDS = []
    

    def __str__(self):
        return f'{self.name}'
    
    def clean(self) -> None:

        self.name = self.name.strip()
        
        if len(self.name) < 3:
            raise ValidationError(message='user name is too short', code=status.HTTP_400_BAD_REQUEST)

        return super().clean()


class BlacklistedIp(models.Model):
    """
        the blacklisted ips will not be able to use the service anymore
    """
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.DO_NOTHING)
    ip_address = models.GenericIPAddressField(null=True, blank=True) 
    datetime = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user}'
