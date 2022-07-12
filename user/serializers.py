from utils.customserializers import DynamicFieldsModelSerializer

from . import models

class UserSerializer(DynamicFieldsModelSerializer):

    class Meta:

        model = models.User
        exclude=('ip_address', 'email')
