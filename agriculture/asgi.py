import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agriculture.settings')
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.layers import get_channel_layer
from channels.auth import AuthMiddlewareStack
from agriculture.device.routing import websocket_urlpatterns

django.setup()  

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})

channel_layer = get_channel_layer()
