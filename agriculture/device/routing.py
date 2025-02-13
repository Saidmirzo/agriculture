from django.urls import re_path

from agriculture.device.device_log_consumer import DeviceLogConsumer
from .consumers import DeviceConsumer

websocket_urlpatterns = [
    re_path(r"ws/device/(?P<device_id>[\w-]+)/$", DeviceConsumer.as_asgi()),
    re_path(r"ws/device-logs/$", DeviceLogConsumer.as_asgi()),
]
