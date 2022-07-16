from django.core.exceptions import ValidationError

from rest_framework import status, serializers

from .models import User, BlacklistedIp
from utils.customserializers import DynamicFieldsModelSerializer

from django.conf import settings

class UserSerializer(DynamicFieldsModelSerializer):

    avatar = serializers.SerializerMethodField()

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
        
        if 'name' in attrs:
            attrs['name'] = attrs['name'].strip()

            if len(attrs['name']) < 3:
                raise ValidationError(message='name too short', code=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(name__iexact=attrs['name']):
                raise ValidationError(message='This name is taken', code=status.HTTP_400_BAD_REQUEST)

        return super().validate(attrs)

    def get_avatar(self, obj):

        if obj.avatar:
            return settings.MEDIA_DOMAIN+obj.avatar.url
        else:
            return None

class BanUserSerializer(serializers.ModelSerializer):


    class Meta:
        
        model = BlacklistedIp
        fields = '__all__'

        extra_kwargs = {
            'ip_address': {'read_only': 'true'},
            'datetime': {'read_only': 'true'}
        }