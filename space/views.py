from django.db.models import Q, Max

from rest_framework import generics, mixins, status, permissions
from rest_framework.response import Response


class MessageListView(generics.GenericAPIView, mixins.ListModelMixin):

    """
        lists the messages between two users if someone else tries to access the room sends forbidden error
    """

    serializer_class = MessagesSerializer
    lookup_field = 'room'
    permission_classes = [permissions.IsAuthenticated]
    

    def get_queryset(self):
         # serialize only undeleted messages, where either of them is sender or receiver

        return Message.objects.filter(Q(sender=self.request.user, sender_deleted=False)|Q(recipient=self.request.user, recipient_deleted=False), room__id=self.kwargs['room']).order_by('-datetime')

    def get(self, request, room, *args, **kwargs):
        
        if not (Room.objects.filter(Q(user1=request.user)|Q(user2=request.user), id=self.kwargs['room'])):
            # if the user is not a participant of the room send 404 response
            return Response(status=status.HTTP_404_NOT_FOUND) # status.HTTP_403_FORBIDDEN


        return self.list(request, room, *args, **kwargs)


class MessageMarkRead(generics.GenericAPIView, mixins.UpdateModelMixin):

    """
        Marks messages by recipient as read 
    """

    serializer_class = PutMessagesSerializer  # Temp fix might want to use MessageSerializer, problem was that an ordered dict was being passed without id field might want to look up the problem later
    queryset = Message.objects.all()
    lookup_field = 'room'
    permission_classes = [permissions.IsAuthenticated]

    def validate_room(self, room):
        try:
            Room.objects.get(id=self.kwargs['room'])

        except Room.DoesNotExist:
            raise status.HTTP_400_BAD_REQUEST

        return True


    def put(self, request, *args, **kwargs):
   
        self.validate_room(kwargs['room'])

        room=Room.objects.get(id=self.kwargs['room'])
        messages = Message.objects.filter(room=room, recipient=self.request.user, recipient_read=False)
        
        instances = []
        for obj in messages:
            obj.recipient_read = True
            obj.save()
            instances.append(obj)

        serializer = MessagesSerializer(instances, many=True, context={'request': request})

        return Response(serializer.data)



