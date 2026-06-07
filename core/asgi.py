"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# application = get_asgi_application()


import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from agriculture.device.routing import websocket_urlpatterns  # Import WebSocket routes
import sys
try:
    import pysqlite3
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

django.setup()  


application = ProtocolTypeRouter({
    "http": get_asgi_application(), 
    "websocket": URLRouter(websocket_urlpatterns),  # Handles WebSocket connections
})