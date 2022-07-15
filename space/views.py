from django.db.models import Q, Max

from rest_framework.response import Response
from rest_framework import generics, mixins, status, permissions

from utils.permissions import AnyOneButBannedPermission, ModeratorPermission, OnlyRegisteredPermission
from utils.exceptions import Forbidden, AuthRequired

from .models import Space, Message
from .serializers import SpaceSerializer, MessageSerializer



# ------------------------------------- Space Views ---------------------------
class CreateSpaceView(generics.GenericAPIView, mixins.CreateModelMixin):

    """
        registered users can create new space
    """

    queryset = Space.objects.all()
    serializer_class = SpaceSerializer
    permission_classes = [AnyOneButBannedPermission | OnlyRegisteredPermission]

    def post(self, request, *args, **kwargs):
        self.create(request, *args, **kwargs)


class UpdateSpaceView(generics.GenericAPIView, mixins.UpdateModelMixin):

    """
        Allows moderators to update the icon, theme, tag line etc
    """

    queryset = Space.objects.all()
    serializer_class = Space
    permission_classes = [ModeratorPermission]
    lookup_field = 'space'

    def put(self, request, *args, **kwargs):
        self.partial_update(request, *args, **kwargs)


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




# class MessageMarkRead(generics.GenericAPIView, mixins.UpdateModelMixin):

#     """
#         Marks messages by recipient as read 
#     """

#     serializer_class = MessageSerializer  # Temp fix might want to use MessageSerializer, problem was that an ordered dict was being passed without id field might want to look up the problem later
#     queryset = Message.objects.all()
#     lookup_field = 'room'
#     permission_classes = [permissions.IsAuthenticated]

#     def validate_room(self, room):
#         try:
#             Room.objects.get(id=self.kwargs['room'])

#         except Room.DoesNotExist:
#             raise status.HTTP_400_BAD_REQUEST

#         return True


#     def put(self, request, *args, **kwargs):
   
#         self.validate_room(kwargs['room'])

#         room=Room.objects.get(id=self.kwargs['room'])
#         messages = Message.objects.filter(room=room, recipient=self.request.user, recipient_read=False)
        
#         instances = []
#         for obj in messages:
#             obj.recipient_read = True
#             obj.save()
#             instances.append(obj)

#         serializer = MessagesSerializer(instances, many=True, context={'request': request})

#         return Response(serializer.data)



