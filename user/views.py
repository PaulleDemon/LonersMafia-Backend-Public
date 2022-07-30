from ipware import get_client_ip

from django.contrib.auth import login, logout, authenticate
from django.db.models import Q

from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics, mixins, status, permissions

from utils.permissions import AnyOneButBannedPermission, IsStaffPermission, IsUsersObjectPermission

from .models import User, BlacklistedIp
from .serializers import BanUserSerializer, UserCreateSerializer, UserLoginSerializer, UserSerializer



# ------------------------------------- user Views ---------------------------
# class LoginUserView(generics.GenericAPIView, mixins.ListModelMixin):

#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [AnyOneButBannedPermission]

#     def get(self, request, *args, **kwargs):

#         ip_address, is_routable = get_client_ip(request)

#         if ip_address:

#             if BlacklistedIp.objects.filter(ip_address=ip_address):
#                 return Response({'banned': 'you are banned from loners. Look what you have done to yourself. Be a good loner next time.'}, status=status.HTTP_417_EXPECTATION_FAILED)

#             try:
#                 user = User.objects.get(ip_address=ip_address)
#                 # logout(request) # don't log them out else sessionif will be lost
#                 login(request, user)
#                 serialized = self.get_serializer(instance=user)

#                 return Response(serialized.data, status=status.HTTP_200_OK)

#             except (User.DoesNotExist, User.MultipleObjectsReturned) as e:
#                 # print("Error: ", e)
#                 return Response({'doesn\'t exist': 'User doesn\'t exist'}, status=status.HTTP_401_UNAUTHORIZED)

#         return Response({'ip error': 'Your ip address is missing or fishy'}, status=status.HTTP_401_UNAUTHORIZED)


class LoginUserView(generics.GenericAPIView, mixins.CreateModelMixin):

    """
        login view
    """

    queryset = User.objects.all()
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):

        ip_address, is_routable = get_client_ip(request)

        name = request.data.get("name")
        password = request.data.get("password")

        if BlacklistedIp.objects.filter(Q(ip_address=ip_address) | Q(user__name=name)):
            return Response({'banned': 'you are banned from loners. Look what you have done to yourself. Be a good loner next time.'}, status=status.HTTP_417_EXPECTATION_FAILED)

      
        user = authenticate(name=name, password=password)

        # logout(request) # don't log them out else sessionif will be lost
        if user:
            login(request, user)
            serialized = self.get_serializer(instance=user)

            return Response(serialized.data, status=status.HTTP_200_OK)

        else:
            # print("Error: ", e)
            return Response({'doesn\'t exist': 'User doesn\'t exist'}, status=status.HTTP_401_UNAUTHORIZED)


class CreateUserView(generics.GenericAPIView, mixins.CreateModelMixin):

    """
        allow creation of user
    """

    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AnyOneButBannedPermission]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        ip_address, is_routable = get_client_ip(request)
        
        if ip_address:

            # print("SErialized data: ", serializer.data)
            user.ip_address = ip_address
            user.save()
            # user = User.objects.create(**serializer.data, ip_address=ip_address)
            
        headers = self.get_success_headers(serializer.data)

        login(request, user)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    

class UpdateUserView(generics.GenericAPIView, mixins.UpdateModelMixin):

    """
        Allows user to update their avatar and tag
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsUsersObjectPermission]
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        
        if 'name' in request.data:
            return Response({'update failed': 'name cannot be changed'}, status=status.HTTP_400_BAD_REQUEST)

        return self.partial_update(request, *args, **kwargs)


class GetUserView(generics.GenericAPIView, mixins.RetrieveModelMixin):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AnyOneButBannedPermission]
    lookup_field = 'name'

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


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

        BlacklistedIp.objects.create(user=user, ip_address=user.ip_address)

        logout(request)
        # if request.query_params.get('delete') == 'true':

        # user.delete()
        return Response(status=status.HTTP_201_CREATED)
