import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Device, DeviceLog
from .serializers import DeviceSerializer, DeviceLogSerializer

channel_layer = get_channel_layer()


def send_device_update():
    """Send device updates via WebSocket"""
    devices = Device.objects.prefetch_related("logs").all()
    data = {
        "type": "update_devices",
        "devices": DeviceSerializer(devices, many=True).data
    }
    
    async_to_sync(channel_layer.group_send)("device_logs_group", {"type": "send_data", "message": json.dumps(data)})


@receiver(post_save, sender=Device)
def device_updated(sender, instance, **kwargs):
    """Trigger WebSocket update when a device is created or updated"""
    send_device_update()


@receiver(post_save, sender=DeviceLog)
def device_log_created(sender, instance, **kwargs):
    """Trigger WebSocket update when a new log is added"""
    send_device_update()