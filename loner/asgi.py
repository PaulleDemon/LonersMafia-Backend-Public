"""
ASGI config for loner project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os
from .wsgi import * # important for production


from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from channels.auth import AuthMiddlewareStack

import mafia.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loner.settings') # if wsgi is not imported first then move this above mafia.routing, this will set settings path to env variable


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator( 
                AuthMiddlewareStack(
                    URLRouter(
                        mafia.routing.websocket_urlpatterns
                     )
                )
            ),
})