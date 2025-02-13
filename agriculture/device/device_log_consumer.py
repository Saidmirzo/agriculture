import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class DeviceLogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Connect WebSocket and join a group to receive updates."""
        self.group_name = "device_logs"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Remove the connection from the group."""
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """Handle incoming messages from the WebSocket (if needed)."""
        pass

    async def send_log_update(self, event):
        from agriculture.models import Device
        """Send updated log data to WebSocket clients."""
        devices = await sync_to_async(list)(Device.objects.all())
        data = [
            {
                "id": device.id,
                "name": device.name,
                "device_id": device.device_id,
                "connection_status": device.connection_status,
                "last_connected": device.last_connected.strftime("%Y-%m-%d %H:%M:%S") if device.last_connected else "N/A",
                "latitude": device.latitude,
                "longitude": device.longitude,
                "logs": json.loads(device.logs) if device.logs else [],
            }
            for device in devices
        ]
        await self.send(text_data=json.dumps({"devices": data}))