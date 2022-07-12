from rest_framework import serializers

from utils.customserializers import DynamicFieldsModelSerializer

from . import models


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

    class Meta:

        model = models.Message
        fields = '__all__'
