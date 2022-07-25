from django.conf import settings
from collections import OrderedDict
from django.forms import ValidationError
from rest_framework import serializers, status

from utils.customserializers import DynamicFieldsModelSerializer

from . import models
from user.models import User
from user.serializers import UserSerializer


REACTIONS = ['🚀', '😭', '🤣', '👎']


class MafiaSerializer(DynamicFieldsModelSerializer):

    is_mod = serializers.SerializerMethodField()
    is_staff = serializers.SerializerMethodField()

    rules = serializers.SerializerMethodField()
    mods = serializers.SerializerMethodField()

    class Meta:

        model = models.Mafia
        exclude = ('created_by', 'created_datetime')
        extra_kwargs = {
            'created_by': {'read_only': True},

            'name': {
                'error_messages': {
                    'required': 'mafia\'s name is required',
                },
            },
            'color_theme': {
                'error_messages': {
                    'required': 'mafia\'s color theme is required',
                },
            },
            
            'icon': {
                'error_messages': {
                    'required': 'mafia\'s icon is required',
                },
            },
            
            'background_image': {
                'error_messages': {
                    'required': 'mafia\'s background image is required',
                },
            },
        }

    def validate(self, attrs):

        if 'name' in attrs:

            attrs['name'] = attrs['name'].strip()
            
            if len(attrs['name']) < 3:
                raise ValidationError('must have atleast 3 characters')

        return super().validate(attrs)

    def get_rules(self, obj):
        """
            gets the rules for the mafia
        """
        return RuleSerializer(models.Rule.objects.filter(mafia=obj), many=True).data

    def get_is_staff(self, obj):
        """
            returns if the user is staff 
        """
        return User.objects.filter(id=self.context['request'].user.id, is_staff=True).exists()

    def get_mods(self, obj):
        """
            gets moderators of the mafia
        """
        return ModeratorSerializer(models.Moderator.objects.filter(mafia=obj), many=True).data

    def get_is_mod(self, obj):
        """
            returns true if the user is a modertor
        """

        return models.Moderator.objects.filter(mafia=obj, user=self.context['request'].user.id).exists()


class RuleSerializer(serializers.ModelSerializer):

    class Meta:

        model = models.Rule
        fields = '__all__'
        extra_kwargs = {
            'rule': {
                'error_messages': {
                    'required': 'rule cannot be empty'
                }
            },
            'maifa': {
                'error_messages': {
                    'required': 'mafia for rule is required'
                }
            }
        }


class ModeratorSerializer(serializers.ModelSerializer):

    class Meta:

        model = models.Moderator
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):

    user = UserSerializer(fields=('id', 'name', 'avatar_url'), read_only=True)
    is_sender = serializers.SerializerMethodField() # lets user know if the user is the sender

    is_staff = serializers.SerializerMethodField() # lets user know if the message is from staff/moderator
    is_mod = serializers.SerializerMethodField() # lets user know if the message is from mod

    media_url = serializers.SerializerMethodField()
    # reactions_count = serializers.SerializerMethodField()
    reactions = serializers.SerializerMethodField()

    class Meta:

        model = models.Message
        fields = '__all__'

        extra_kwargs = {
            'datetime': {'read_only': True},
            'user': {'read_only': True},
        }

    def get_media_url(self, obj):
        
        if obj.media:
            return settings.MEDIA_DOMAIN+obj.media.url

    def get_is_sender(self, obj):

        request = self.context.get('request')
        user = request.user.id if request else self.context.get('user')

        return models.Message.objects.filter(id=obj.id, user=user).exists()

    def get_is_mod(self, obj):
        """
            returns true if the user is a modertor
        """
        # request = self.context.get('request')
        # user = request.user.id if request else self.context.get('user')

        return models.Moderator.objects.filter(mafia=obj.mafia, user=obj.user).exists()

    def get_is_staff(self, obj):
        """
            returns if the user is staff 
        """
        # request = self.context.get('request')
        # user = request.user.id if request else self.context.get('user')

        return User.objects.filter(id=obj.user.id, is_staff=True).exists()


    def get_reactions(self, obj):

        """
            gets the list of reaction by the user
        """

        request = self.context.get('request')
        user = request.user.id if request else self.context.get('user')

        # instance = models.Reaction.objects.filter(message=obj, reaction__in=REACTIONS).distinct('reaction')

        serializer = []

        for x in REACTIONS:
            instance = models.Reaction.objects.filter(message=obj, reaction=x).distinct('reaction') 

            if instance.exists():
                serializer += ReactionSerializer(instance=instance, context={'user': user}, 
                                many=True, fields=('id', 'reaction', 'is_reacted', 'reaction_count')).data

            else: 
                # if the reaction doens't exist yet in the database the return this default
                serializer += [OrderedDict({'id': None, 'is_reacted': False, 'reaction_count': 0, 'reaction': x})]

        # return ReactionSerializer(instance=instance, context={'user': user},
        #                                 many=True, fields=('reaction', 'is_reacted', 'reaction_count')).data
        return serializer


class ReactionSerializer(DynamicFieldsModelSerializer):

    is_reacted = serializers.SerializerMethodField()
    reaction_count = serializers.SerializerMethodField()

    class Meta:

        model = models.Reaction
        fields = '__all__'

    def validate(self, attrs):

        if attrs['reaction'] not in REACTIONS:
            raise ValidationError(message=f'This reaction is not allowed yet, allowed reactions are {",".join(REACTIONS)}')


        if models.Reaction.objects.filter(user=self.context['request'].user.id, 
                            message=attrs['message'], reaction=attrs['reaction']).exists():
            
            raise ValidationError('The user has already reacted to this message', code=status.HTTP_400_BAD_REQUEST)

        return super().validate(attrs)

    def get_is_reacted(self, obj):

        request = self.context.get('request')
        user = request.user.id if request else self.context.get('user')

        return models.Reaction.objects.filter(user=user, message=obj.message, reaction=obj.reaction).exists()
    
    def get_reaction_count(self, obj):
        return models.Reaction.objects.filter(message=obj.message, reaction=obj.reaction).count()
