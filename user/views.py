from ipware import get_client_ip

from django.forms import ValidationError
from django.contrib.auth import login, logout

from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics, mixins, status

from utils.permissions import AnyOneButBannedPermission, IsStaffPermission, IsUsersObjectPermission

from .models import User, BlacklistedIp
from .serializers import BanUserSerializer, UserSerializer



# ------------------------------------- user Views ---------------------------
class LoginUserView(generics.GenericAPIView, mixins.ListModelMixin):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AnyOneButBannedPermission]

    def get(self, request, *args, **kwargs):

        ip_address, is_routable = get_client_ip(request)

        try:
            user = User.objects.get(ip_address=ip_address)
            logout(request) # log them out before logging them in
            login(request, user)
            serialized = self.get_serializer(instance=user)

            return Response(serialized.data, status=status.HTTP_200_OK)

        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return Response({'doesn\'t exist': 'User doesn\'t exist'}, status=status.HTTP_401_UNAUTHORIZED)


class CreateUserView(generics.GenericAPIView, mixins.CreateModelMixin):

    """
        allow creation of user
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AnyOneButBannedPermission]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ip_address, is_routable = get_client_ip(request)

        if ip_address:
     
            # print("SErialized data: ", serializer.data)
            user = serializer.save()
            user.ip_address = ip_address
            user.save()
            # user = User.objects.create(**serializer.data, ip_address=ip_address)
            headers = self.get_success_headers(serializer.data)
            login(request, user)

            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
        return Response(status.HTTP_400_BAD_REQUEST) 
    

class UpdateUserView(generics.GenericAPIView, mixins.UpdateModelMixin):

    """
        Allows user to update their avatar and tag
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsUsersObjectPermission]
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        
        if 'name' in request.data:
            return Response({'update failed': 'name cannot be changed'}, status=status.HTTP_400_BAD_REQUEST)

        return self.partial_update(request, *args, **kwargs)


class BanUserFromNetworkView(generics.GenericAPIView, mixins.CreateModelMixin):

    """
        Ban the user from loner. only staff.
    """

    queryset = BlacklistedIp.objects.all()
    serializer_class = BanUserSerializer
    permission_classes = [IsStaffPermission]

    def post(self, request, *args, **kwargs):
 
        user = request.data.get('user')

        try:
            user = User.objects.get(id=user)

        except User.DoesNotExist:
            return Response({'detail': 'user doesn\'t exist'}, status=status.HTTP_404_NOT_FOUND)

        BlacklistedIp.objects.create(ip_address=user.ip_address)

        # if request.query_params.get('delete') == 'true':
        user.delete()

        return Response(status=status.HTTP_201_CREATED)
