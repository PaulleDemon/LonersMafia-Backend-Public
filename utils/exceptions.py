from rest_framework.exceptions import APIException
from rest_framework import status


class AuthRequired(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'You need to join loner'
    default_code = 'not_registered'


class BannedFromMafia(APIException):
    status_code = status.HTTP_406_NOT_ACCEPTABLE
    default_detail = 'You are banned from this mafia'
    default_code = 'banned'


class BannedFromLoner(APIException):
    status_code = status.HTTP_417_EXPECTATION_FAILED
    default_detail = 'You are banned from loner for violating its terms'
    default_code = 'banned'


class Forbidden(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'you are forbidden from performing this action'
    default_code = 'forbidden'
