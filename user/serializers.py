from typing import OrderedDict
from django.core.exceptions import ValidationError

from rest_framework import status, serializers

from .models import User, BlacklistedIp
from utils.customserializers import DynamicFieldsModelSerializer

from django.conf import settings



class UserLoginSerializer(serializers.ModelSerializer):

    class Meta:

        model = User
        fields = ('id', 'name', 'password', 'avatar', 'tag_line')
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
            'avatar': {'read_only': True},
            'tag_line': {'read_only': True},
        }


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        
        model = User
        fields = ('id', 'name', 'avatar', 'tag_line', 'password')

        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create(
            name=validated_data.get('name', ''),
            tag_line=validated_data.get('tag_line', ''),
            avatar=validated_data.get('avatar')
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserSerializer(DynamicFieldsModelSerializer):

    avatar_url = serializers.SerializerMethodField()

    class Meta:

        model = User
        fields = ('id', 'name', 'avatar', 'tag_line', 'avatar_url')
        # exclude = ('ip_address', 'email', 'password', 
        #             'last_login', 'is_superuser', 'is_admin', 
        #             'is_active', 'groups', 'date_joined', 'user_permissions'
        #             )
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

    def get_avatar_url(self, obj):
        """
            Gets full url improtant for sending images through sockets
        """
        if isinstance(obj, OrderedDict):
            return None

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