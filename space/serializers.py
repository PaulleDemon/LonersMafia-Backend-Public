from rest_framework import serializers

from utils.customserializers import DynamicFieldsModelSerializer

from . import models
from user.models import User

class SpaceSerializer(DynamicFieldsModelSerializer):

    rules = serializers.SerializerMethodField()
    moderators = serializers.SerializerMethodField()

    class Meta:

        model = models.Space
        fields = '__all__'

    def get_rules(self, obj):
        """
            gets the rules for the space
        """

        return RuleSerializer(models.Rule.objects.get(space=obj), many=True).data

    def get_is_staff(self, obj):
        """
            returns if the user is staff 
        """
        return User.objects.filter(id=self.context['request'].id, staff=True).exists()

    def get_mods(self, obj):
        """
            gets moderators of the space
        """
        return ModeratorSerializer(models.Moderator.objects.get(space=obj), many=True).data

    def is_mod(self, obj):
        """
            returns true if the user is a modertor
        """

        return models.Moderator.objects.filter(space=obj, user=self.context['request'].user.id).exists()


class RuleSerializer(serializers.ModelSerializer):

    class Meta:

        model = models.Rule
        fields = '__all__'


class ModeratorSerializer(serializers.ModelSerializer):

    class Meta:

        model = models.Moderator
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):

    is_staff = serializers.SerializerMethodField() # lets user know if the message is from staff/moderator
    is_mod = serializers.SerializerMethodField() # lets user know if the message is from mod

    class Meta:

        model = models.Message
        fields = '__all__'

    def is_mod(self, obj):
        """
            returns true if the user is a modertor
        """

        return models.Moderator.objects.filter(space=obj, user=self.context['request'].user.id).exists()

    def get_is_staff(self, obj):
        """
            returns if the user is staff 
        """
        return User.objects.filter(id=self.context['request'].id, staff=True).exists()

    def is_mod(self, obj):
        """
            returns true if the user is a modertor
        """

        return models.Moderator.objects.filter(space=obj, user=self.context['request'].user.id).exists()
