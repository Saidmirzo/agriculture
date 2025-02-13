import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class DeviceLogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Connect to WebSocket and join the group"""
        await self.channel_layer.group_add("device_logs", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Leave the WebSocket group when disconnected"""
        await self.channel_layer.group_discard("device_logs", self.channel_name)

    async def send_device_logs(self, event):
        from agriculture.models import Device, DeviceLog
        """Send updated device logs to WebSocket clients"""
        devices = Device.objects.all()
        devices_data = [
            {
                "device_id": device.device_id,
                "name": device.name,
                "connection_status": device.connection_status,
                "last_connected": device.last_connected.isoformat(),
                "latitude": device.latitude,
                "longitude": device.longitude,
                "logs": [log.log for log in device.logs.all()[:10]],  # Fetch only last 10 logs
            }
            for device in devices
        ]

        await self.send(text_data=json.dumps({"devices": devices_data}))