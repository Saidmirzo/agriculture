from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from agriculture.models import Device

def send_log_update():
    """Notify WebSocket clients about log updates."""
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "device_logs",
        {"type": "send_log_update"}
    )

def add_log_to_device(device_id, log_message):
    """Add a log entry to the device and notify WebSockets."""
    device = Device.objects.get(device_id=device_id)
    logs_list = json.loads(device.logs) if device.logs else []
    logs_list.append(log_message)
    logs_list = logs_list[-50:]  # Keep only the last 50 logs
    device.logs = json.dumps(logs_list)
    device.save()
    
    send_log_update()  # Notify WebSocket clients about the update