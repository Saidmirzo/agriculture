from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()

def send_event_to_device(device_id, event_data):
    async_to_sync(channel_layer.group_send)(
        device_id,
        {
            "type": "send_event",
            "event": event_data,
        }
    )
