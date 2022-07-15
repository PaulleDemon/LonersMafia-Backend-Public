from django.core.exceptions import ValidationError

from rest_framework import status

from .models import User
from utils.customserializers import DynamicFieldsModelSerializer


class UserSerializer(DynamicFieldsModelSerializer):

    class Meta:

        model = User
        exclude = ('ip_address', 'email', 'password', 
                    'last_login', 'is_superuser', 'is_admin', 
                    'is_active', 'groups', 'date_joined', 'user_permissions'
                    )
        extra_kwargs = {
            'ip_address': {'read_only': True},
            'is_staff': {'read_only': True},
        }

    def validate(self, attrs):
        
        attrs['name'] = attrs['name'].strip()

        if len(attrs['name']) < 3:
            raise ValidationError(message='name too short', code=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(name__iexact=attrs['name']):
            raise ValidationError(message='This name is taken', code=status.HTTP_400_BAD_REQUEST)

        return super().validate(attrs)