from ipware import get_client_ip

from rest_framework.response import Response
from rest_framework import generics, mixins, status, permissions

from utils.permissions import AnyOneButBannedPermission, ModeratorPermission, OnlyRegisteredPermission, IsStaffPermission

from user.models import User
from .models import Reaction, Space, Message
from .serializers import ReactionSerializer, SpaceSerializer, MessageSerializer



# ------------------------------------- Space Views ---------------------------
class CreateSpaceView(generics.GenericAPIView, mixins.CreateModelMixin):

    """
        registered users can create new space
    """

    queryset = Space.objects.all()
    serializer_class = SpaceSerializer
    permission_classes = [AnyOneButBannedPermission | OnlyRegisteredPermission]

    def post(self, request, *args, **kwargs):
        # created = self.create(request, *args, **kwargs)

        ip_address, is_routable = get_client_ip(request)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        model = Space(**serializer.validated_data)
        
        user = User.objects.filter(ip_address=ip_address)
        
        if user.exists():
            model.created_by = user.first()
            model.save()
            
            new_serializer = SpaceSerializer(model)

            return Response(new_serializer.data, status=status.HTTP_201_CREATED)

        else:
            return Response({'unregistered': 'you need to register before creating a space'}, status=status.HTTP_403_FORBIDDEN)


class UpdateSpaceView(generics.GenericAPIView, mixins.UpdateModelMixin):

    """
        Allows moderators to update the icon, theme, tag line etc
    """

    queryset = Space.objects.all()
    serializer_class = Space
    permission_classes = [ModeratorPermission]
    lookup_field = 'space'

    def put(self, request, *args, **kwargs):

        if 'name' in request.data:
            return Response({'cannot update': 'you cannot update the name of the space'}, code=status.HTTP_400_BAD_REQUEST)

        return self.partial_update(request, *args, **kwargs)


class ListSpaceView(generics.GenericAPIView, mixins.ListModelMixin):

    """
        Lists all the spaces.
    """
    queryset = Space.objects.all()
    serializer_class = SpaceSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        
        list_type = request.query_params.get('type')

        if list_type is None:
            query = self.get_queryset().order_by('-message__datetime')
            serializer = self.get_serializer(query, context={'request': request})

            return Response(serializer.data, status=status.HTTP_200_OK)

        return self.list(request, *args, **kwargs)


# -------------------------------------- Message views ------------------------------
class MessageListView(generics.GenericAPIView, mixins.ListModelMixin):

    """
        lists the messages in the space
    """

    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    lookup_field = 'space'
    permission_classes = [AnyOneButBannedPermission]
    ordering_fields = ['datetime']
    ordering = ['-datetime']

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class MessageCreateView(generics.GenericAPIView, mixins.CreateModelMixin):

    """
        creates message
    """

    permission_classes = [AnyOneButBannedPermission|OnlyRegisteredPermission]
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    lookup_field = 'space'

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class MessageDeleteView(generics.GenericAPIView, mixins.DestroyModelMixin):

    """
        Delete message
    """

    permission_classes = [ModeratorPermission|IsStaffPermission]
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    lookup_field = 'id'

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


# -------------------------------- react view ----------------------

class MessageReactionCreateView(generics.GenericAPIView, mixins.CreateModelMixin):


    permission_classes = [OnlyRegisteredPermission]
    queryset = Reaction.objects.all()
    serializer_class = ReactionSerializer


    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class MessageReactionDeleteView(generics.GenericAPIView, mixins.DestroyModelMixin):

    queryset = Reaction.objects.all()
    serializer_class = ReactionSerializer

    lookup_field = 'id'

    def delete(self, request, *args, **kwargs):

        if Reaction.objects.filter(id=kwargs['id'], user=request.user.id).exists():
            return self.delete(request, *args, **kwargs)

        return Response({'forbidden': 'you are forbidden'}, status=status.HTTP_403_FORBIDDEN)
