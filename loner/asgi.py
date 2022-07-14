"""
ASGI config for loner project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from .auth_middleware import JWTAuthMiddleware

import space.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loner.settings')


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator( 
                JWTAuthMiddleware(
                    URLRouter(
                        space.routing.websocket_urlpatterns
                     )
                )
            ),
})