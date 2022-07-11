from django.db import models
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin



# custom manager
class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where username is the unique identifier.
    """
    def create_user(self, username, ip_address=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not username:
            raise ValueError('The Email must be set')
       
        user = self.model(username=username, **extra_fields)
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


class User(AbstractBaseUser, PermissionsMixin):

    username = models.CharField(unique=True, max_length=30)
    user_avatar = models.FileField() # TODO; from here
    ip_address = models.GenericIPAddressField(null=True) # the ip is stored only to prevent attacks on server


    email = models.EmailField(null=True) # used only for admin users

    objects = CustomUserManager()
    USERNAME_FIELD = 'email' # emails only for admins and staffs
    
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now) # you can also use auto_add_now=True

    def __str__(self):
        return self.username



class BlacklistedIp(models.Model):
    """
        the blacklisted ips will not be able to use the service anymore
    """
    ip_address = models.GenericIPAddressField(null=False) 

    def __str__(self):
        return self.ip_address