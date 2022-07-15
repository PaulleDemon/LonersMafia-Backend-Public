from rest_framework import permissions

from ipware import get_client_ip

from . import exceptions

from space.models import Moderator, BanUserFromSpace
from user.models import User, BlacklistedIp



class OnlyRegisteredPermission(permissions.BasePermission):

    """
        allows only registered users
    """ 

    def has_permission(self, request, view):
        
        ip_address, is_routable = get_client_ip(request)

        if User.objects.filter(ip_address=ip_address).exists():
            return True

        raise exceptions.AuthRequired()


class AnyOneButBannedPermission(permissions.BasePermission):
    """
        prevents unnecessary access from blacklisted ip addresses
    """

    def has_permission(self, request, view):

        ip_address, is_routable = get_client_ip(request)

        if not BlacklistedIp.objects.filter(ip_address=ip_address).exists():
            return True

        raise exceptions.BannedFromLoner()


class IsUsersObjectPermission(OnlyRegisteredPermission):
    """
        Allows only the original author to change the user objects it created
    """

    def has_object_permission(self, request, view, obj):

        ip_address, is_routable = get_client_ip(request)

        if User.objects.filter(name=request.user.name, ip_address=ip_address).exists():
            return True

        raise exceptions.Forbidden(detail='you don\'t have permission to perform this action')


class AnyOneButSpaceBanned(permissions.BasePermission):
    """ users that are banned from space cannot message that space """

    def has_object_permission(self, request, view, obj):

        if (not BanUserFromSpace.objects.filter(user=request.user.id, space=obj.id)):
            return True

        raise exceptions.BannedFromSpace()


class ModeratorPermission(permissions.BasePermission):

    """ moderators of the space are given privilage to delete posts """
   

    def has_object_permission(self, request, view, obj):
        
        if request.user.is_staff or Moderator.objects.filter(space=obj.id, user=request.user.id).exists():
            return True

        raise exceptions.Forbidden()


class IsStaffPermission(permissions.BasePermission):

    def has_permission(self, request, view):

        if request.user.is_staff:
            return True

        raise exceptions.Forbidden()