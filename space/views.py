import json
from datetime import datetime
from ipware import get_client_ip

from django.db.models import Max
from django.shortcuts import get_object_or_404
from django.db.models.functions import Coalesce

from rest_framework.response import Response
from rest_framework import generics, mixins, status, permissions

from utils.permissions import AnyOneButBannedPermission, ModeratorPermission, OnlyRegisteredPermission, IsStaffPermission

from user.models import User
from .models import Moderator, Reaction, Rule, Mafia, Message, BanUserFromSpace
from .serializers import ModeratorSerializer, ReactionSerializer, RuleSerializer, MafiaSerializer, MessageSerializer



# ------------------------------------- Space Views ---------------------------
class CreateMafiaView(generics.GenericAPIView, mixins.CreateModelMixin):

    """
        registered users can create new mafia
    """

    queryset = Mafia.objects.all()
    serializer_class = MafiaSerializer
    permissions.IsAuthenticated
    permission_classes = [permissions.IsAuthenticated, AnyOneButBannedPermission, OnlyRegisteredPermission]

    def post(self, request, *args, **kwargs):
        # created = self.create(request, *args, **kwargs)

        ip_address, is_routable = get_client_ip(request)

        rules = [] 
        if request.data.get("rules"):
            # https://stackoverflow.com/questions/44717442/this-querydict-instance-is-immutable
            data = request.data
            _mutable = data._mutable
            data._mutable = True

            rules = json.loads(data.pop("rules")[0])# the list is recieved from front-end in the form of json array

            rules = [rule for rule in rules if rule != ''] # remove empty strings from rules

            data._mutable = _mutable



        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        model = Mafia(**serializer.validated_data)
        
        user = User.objects.filter(ip_address=ip_address)
        
        if user.exists():
            model.created_by = user.first()
            try:
                model.save()
                
                if len(rules) > 5:
                    return Response({'bad request': 'only 5 rules allowed'}, status=status.HTTP_400_BAD_REQUEST)

                for rule in rules: 
                    rule_serializer = RuleSerializer(data={'mafia': model.id, 'rule': rule})
                    rule_serializer.is_valid(raise_exception=True)
                    rule_serializer.save()

            except (Exception) as e:
                pass

            new_serializer = MafiaSerializer(model, context={'request': request})

            return Response(new_serializer.data, status=status.HTTP_201_CREATED)

        else:
            return Response({'unregistered': 'you need to register before creating a mafia'}, status=status.HTTP_403_FORBIDDEN)


class UpdateMafiaView(generics.GenericAPIView, mixins.UpdateModelMixin):

    """
        Allows moderators to update the icon, theme, tag line etc
    """

    queryset = Mafia.objects.all()
    serializer_class = MafiaSerializer
    permission_classes = [permissions.IsAuthenticated, ModeratorPermission]
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):

        if 'name' in request.data:
            return Response({'cannot update': 'you cannot update the name of the mafia'}, status=status.HTTP_400_BAD_REQUEST)

        rules = [] 
        if request.data.get("rules"):
            # https://stackoverflow.com/questions/44717442/this-querydict-instance-is-immutable
            data = request.data
            _mutable = data._mutable
            data._mutable = True

            rules = json.loads(data.pop("rules")[0])# the list is recieved from front-end in the form of json array

            rules = [rule for rule in rules if rule != ''] # remove empty strings from rules

            data._mutable = _mutable

        if rules:
            
            if len(rules) > 5:
                return Response({'bad request': 'only 5 rules allowed'}, status=status.HTTP_400_BAD_REQUEST)
            
            Rule.objects.filter(mafia=kwargs['id']).delete()
            
            for rule in rules: 
                rule_serializer = RuleSerializer(data={'mafia': kwargs['id'], 'rule': rule})
                rule_serializer.is_valid(raise_exception=True)
                rule_serializer.save()


        return self.partial_update(request, *args, **kwargs)


class ListMafiaView(generics.GenericAPIView, mixins.ListModelMixin, mixins.RetrieveModelMixin):

    """
        Lists or gets the mafia.
    """
    queryset = Mafia.objects.all()
    serializer_class = MafiaSerializer
    permission_classes = [permissions.AllowAny]
    ordering = ['-created_datetime']
    lookup_field = 'name'

    def valdate_query_params(self):

        user = self.request.query_params.get('user')
        # list_type = self.request.query_params.get('sort')

        try:
            
            if user:
                int(user)
        
        except (ValueError, TypeError):
            return False

        return True

    def get(self, request, *args, **kwargs):
        
        if kwargs.get('name'):
            return self.retrieve(request, *args, **kwargs)

        if not self.valdate_query_params():
            return Response({'invalid paramaters': 'invalid query parameters'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.query_params.get('user')
        sort = request.query_params.get('sort')

        if sort is None:
            query = self.get_queryset().order_by('-message__datetime')
            paginated_queryset = self.paginate_queryset(query)
            serializer = self.get_serializer(paginated_queryset, context={'request': request}, many=True)

            return self.get_paginated_response(serializer.data)
            # return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            
            if sort in ['recent', 'moderating']:

                try:
                    int(user)
                
                except (ValueError, TypeError):

                    return Response({'bad request': 'invalid user'}, status=status.HTTP_400_BAD_REQUEST)

                if sort == 'recent':
                    sub_query = Mafia.objects.filter(message__user=user).order_by('-id').distinct('id')
                    query = Mafia.objects.filter(id__in=sub_query).annotate(latest=Max('message__datetime')).order_by('-latest', '-id')
                    # print("User: ", sub_query)

                elif sort == 'moderating':
                    sub_query = Mafia.objects.filter(moderator__user=user).order_by('id', '-moderator__datetime').distinct('id')
                    query = Mafia.objects.filter(id__in=sub_query).order_by('-moderator__datetime', 'id')

            elif sort == 'trending':
                # sub_query = Space.objects.order_by('id', '-message__datetime').distinct('id') # you can't use distinct with order_by hence the hack
                # query = Space.objects.filter(id__in=sub_query).annotate(latest=Max('message__datetime')).order_by('latest', 'id')
                query = Mafia.objects.annotate(latest=Max(Coalesce('message__datetime', datetime.min))).order_by('-latest', 'id')

            else:
                query = Mafia.objects.all().order_by('-created_datetime', 'id')

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
        lists the messages in the Mafia
    """

    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    lookup_field = 'mafia'
    permission_classes = [AnyOneButBannedPermission]
    ordering_fields = ['datetime']
    ordering = ['-datetime']

    def get_queryset(self):
        return Message.objects.filter(mafia=self.kwargs['mafia']).order_by('-datetime')

    def get(self, request, *args, **kwargs):
        
        # if not Space.objects.filter(name=kwargs.get('space')).exists():
        #     return Response({'doesn\'t exist': 'This space doesn\'t exist'}, status=status.HTTP_404_NOT_FOUND)

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

        msg = Message(**serializer.validated_data)
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
                Moderator.objects.filter(user__in=message.values('user'), mafia__in=message.values('mafia')).exists()):
            return Response({'forbidden': 'only staff can delete other moderators messaeges'}, status=status.HTTP_403_FORBIDDEN)

        return self.destroy(request, *args, **kwargs)


# -------------------------------- staff/mod option view ----------------
class ModOptionsView(generics.GenericAPIView, mixins.CreateModelMixin):

    """
        query_param: deleteAll - set this to true if you want to delete all the messages of the user in the mafia

        structure: {
            id: <- message id,
            mafia: <- mafia,
            user: <- user who sent that message
        }
    """

    permission_classes=[permissions.IsAuthenticated, ModeratorPermission|IsStaffPermission]

    def post(self, request, *args, **kwargs):

        if 'user' not in request.data or 'mafia' not in request.data or 'id' not in request.data:
            return Response(data={'bad request': 'incorrect data'}, status=status.HTTP_400_BAD_REQUEST)

        msg_id = request.data.get('id')
        user = request.data.get('user')
        mafia = request.data.get('mafia')

        if request.query_params.get('deleteAll') == 'true':
            Message.objects.filter(user=user, mafia=mafia).delete()

        else:
            Message.objects.filter(id=msg_id).delete()

        BanUserFromSpace.objects.create(user=request)

        return Response({'success': 'ban successful'}, status=status.HTTP_200_OK)

# -------------------------------- react view ----------------------

class MessageReactionCreateView(generics.GenericAPIView, mixins.CreateModelMixin):


    permission_classes = [permissions.IsAuthenticatedOrReadOnly, OnlyRegisteredPermission]
    queryset = Reaction.objects.all()
    serializer_class = ReactionSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class MessageReactionDeleteView(generics.GenericAPIView, mixins.DestroyModelMixin):

    queryset = Reaction.objects.all()
    serializer_class = ReactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    lookup_fields = ['message', 'reaction']

    def get_object(self):
        queryset = self.get_queryset()             # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends
        filter = {}
        for field in self.lookup_fields:
            try:                                  # Get the result with one or more fields.
                filter[field] = self.kwargs[field]
            except Exception:
                pass
        return get_object_or_404(queryset, **filter)  # Lookup the object

    def get_queryset(self):

        return Reaction.objects.filter(reaction=self.kwargs['reaction'], message=self.kwargs['message'], user=self.request.user)

    def delete(self, request, *args, **kwargs):

        return self.destroy(request, *args, **kwargs)
