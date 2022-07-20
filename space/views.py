from genericpath import exists
from ipware import get_client_ip

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, mixins, status, permissions

from utils.permissions import AnyOneButBannedPermission, ModeratorPermission, OnlyRegisteredPermission, IsStaffPermission

from user.models import User
from .models import Moderator, Reaction, Space, Message, BanUserFromSpace
from .serializers import ModeratorSerializer, ReactionSerializer, SpaceSerializer, MessageSerializer



# ------------------------------------- Space Views ---------------------------
class CreateSpaceView(generics.GenericAPIView, mixins.CreateModelMixin):

    """
        registered users can create new space
    """

    queryset = Space.objects.all()
    serializer_class = SpaceSerializer
    permissions.IsAuthenticated
    permission_classes = [permissions.IsAuthenticated, AnyOneButBannedPermission, OnlyRegisteredPermission]

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

    def valdate_query_params(self):

        user = self.request.query_params.get('user')
        # list_type = self.request.query_params.get('sort')

        try:
            
            if user:
                int(user)
        
        except ValueError:
            return False

        return True

    def get(self, request, *args, **kwargs):
        
        if kwargs.get('name'):
            return self.retrieve(request, *args, **kwargs)

        if not self.valdate_query_params():
            return Response({'invalid paramaters': 'invalid query parameters'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.query_params.get('user')
        list_type = request.query_params.get('sort')

        if list_type is None:
            query = self.get_queryset().order_by('-message__datetime')
            paginated_queryset = self.paginate_queryset(query)
            serializer = self.get_serializer(paginated_queryset, context={'request': request}, many=True)

            return self.get_paginated_response(serializer.data)
            # return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            
            if list_type == 'recent':
                sub_query = Space.objects.filter(message__user=user).order_by('id', '-message__datetime').distinct('id')
                query = Space.objects.filter(id__in=sub_query).order_by('-message__datetime')

            elif list_type == 'moderating':
                sub_query = Space.objects.filter(moderator__user=user).order_by('id', '-moderator__datetime').distinct('id')
                query = Space.objects.filter(id__in=sub_query).order_by('-moderator__datetime')

            elif list_type == 'trending':
                sub_query = Space.objects.order_by('id', '-message__datetime').distinct('id') # you can't use distinct with order_by hence the hack
                query = Space.objects.filter(id__in=sub_query).order_by('-message__datetime')

            else:
                query = Space.objects.all().order_by('-created_datetime')

            paginated_queryset = self.paginate_queryset(query)
            serializer = self.get_serializer(paginated_queryset, context={'request': request}, many=True)

            return self.get_paginated_response(serializer.data)

        # return self.list(request, *args, **kwargs)


class AssignModView(generics.GenericAPIView, mixins.CreateModelMixin):

    queryset = Moderator.objects.all()
    serializer_class = ModeratorSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffPermission|ModeratorPermission]

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


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
    
    permission_classes = [permissions.IsAuthenticated, AnyOneButBannedPermission, OnlyRegisteredPermission]
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
                request.user and not request.user.is_staff and  
                Moderator.objects.filter(user__in=message.values('user'), space__in=message.values('space')).exists()):
            return Response({'forbidden': 'only staff can delete other moderators messaeges'}, status=status.HTTP_403_FORBIDDEN)

        return self.destroy(request, *args, **kwargs)


# -------------------------------- staff/mod option view ----------------
class ModOptionsView(generics.GenericAPIView, mixins.CreateModelMixin):

    """
        query_param: deleteAll - set this to true if you want to delete all the messages of the user in the space

        structure: {
            id: <- message id,
            space: <- space,
            user: <- user who sent that message
        }
    """

    permission_classes=[permissions.IsAuthenticated, ModeratorPermission|IsStaffPermission]

    def post(self, request, *args, **kwargs):

        if 'user' not in request.data or 'space' not in request.data or 'id' not in request.data:
            return Response(data={'bad request': 'incorrect data'}, status=status.HTTP_400_BAD_REQUEST)

        msg_id = request.data.get('id')
        user = request.data.get('user')
        space = request.data.get('space')

        if request.query_params.get('deleteAll') == 'true':
            Message.objects.filter(user=user, space=space).delete()

        else:
            Message.objects.filter(id=msg_id).delete()

        BanUserFromSpace.objects.create(user=request)

        return Response({'success': 'ban successful'}, status=status.HTTP_200_OK)

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
