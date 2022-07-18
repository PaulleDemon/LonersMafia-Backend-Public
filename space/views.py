from genericpath import exists
from ipware import get_client_ip

from rest_framework.response import Response
from rest_framework import generics, mixins, status, permissions

from utils.permissions import AnyOneButBannedPermission, ModeratorPermission, OnlyRegisteredPermission, IsStaffPermission

from user.models import User
from .models import Moderator, Reaction, Space, Message
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
    serializer_class = SpaceSerializer
    permission_classes = [ModeratorPermission]
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):

        if 'name' in request.data:
            return Response({'cannot update': 'you cannot update the name of the space'}, status=status.HTTP_400_BAD_REQUEST)

        return self.partial_update(request, *args, **kwargs)


class ListSpaceView(generics.GenericAPIView, mixins.ListModelMixin, mixins.RetrieveModelMixin):

    """
        Lists or gets the spaces.
    """
    queryset = Space.objects.all()
    serializer_class = SpaceSerializer
    permission_classes = [permissions.AllowAny]
    ordering = ['-created_datetime']
    lookup_field = 'name'

    def get(self, request, *args, **kwargs):
        
        if kwargs.get('name'):
            return self.retrieve(request, *args, **kwargs)

        list_type = request.query_params.get('type')

        if list_type is None:
            query = self.get_queryset().order_by('-message__datetime')
            serializer = self.get_serializer(query, context={'request': request}, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        return self.list(request, *args, **kwargs)


class BanFromSpaceView():
    pass


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

    def get_queryset(self):
        return Message.objects.filter(space__name=self.kwargs['space']).order_by('-datetime')

    def get(self, request, *args, **kwargs):
        
        if not Space.objects.filter(name=kwargs.get('space')).exists():
            return Response({'doesn\'t exist': 'This space doesn\'t exist'}, status=status.HTTP_404_NOT_FOUND)

        return self.list(request, *args, **kwargs)


class MessageCreateView(generics.GenericAPIView, mixins.CreateModelMixin):

    """
        creates message
    """

    permission_classes = [AnyOneButBannedPermission|OnlyRegisteredPermission]
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    # lookup_field = 'space'

    def post(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        msg = serializer.save()
        msg.user = self.request.user
        msg.save()

        new_serializer = self.get_serializer(msg, context={'request': request})

        return Response(new_serializer.data, status=status.HTTP_201_CREATED)


class MessageDeleteView(generics.GenericAPIView, mixins.DestroyModelMixin):

    """
        Delete message
    """

    permission_classes = [ModeratorPermission|IsStaffPermission]
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    lookup_field = 'id'

    def delete(self, request, *args, **kwargs):

        message = Message.objects.filter(id=kwargs['id'])

        if (message.first() and message.first().user != request.user and 
                Moderator.objects.filter(user__in=message.values('user'), space__in=message.values('space')).exists()):
            return Response({'forbidden': 'only staff can delete other moderators messaeges'}, status=status.HTTP_403_FORBIDDEN)

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
