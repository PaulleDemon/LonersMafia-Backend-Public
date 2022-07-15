from django.db.models import Q, Max

from rest_framework.response import Response
from rest_framework import generics, mixins, status, permissions

from utils.permissions import AnyOneButBannedPermission, ModeratorPermission, OnlyRegisteredPermission
from utils.exceptions import Forbidden, AuthRequired

from .models import User, BlacklistedIp
from .serializers import UserSerializer

from ipware import get_client_ip


# ------------------------------------- user Views ---------------------------
class CreateUserView(generics.GenericAPIView, mixins.CreateModelMixin):

    """
        allow creation of user
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AnyOneButBannedPermission]

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ip_address, is_routable = get_client_ip(request)

        if ip_address:

            User.objects.create(**serializer.data, ip_address=ip_address)
            
            headers = self.get_success_headers(serializer.data)
            return Response(status=status.HTTP_201_CREATED, headers=headers)
    
        return Response(status.HTTP_400_BAD_REQUEST) 
    
class UpdateUserView(generics.GenericAPIView, mixins.UpdateModelMixin):

    """
    """