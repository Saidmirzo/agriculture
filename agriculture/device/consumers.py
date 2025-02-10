import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now
from asgiref.sync import sync_to_async

class DeviceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.device_id = self.scope["url_route"]["kwargs"]["device_id"]
        self.group_name = f"device_{self.device_id}"  # Each device joins its own group
        
        await self.accept()

        # Update device status to online
        device, created = await self.get_or_create_device(self.device_id)
        device.connection_status = True
        device.last_connected = now()
        await self.save_device(device)

        # Add device to its own WebSocket group
        print(f"✅ Adding device {self.device_id} to group: {self.group_name}")
        await self.channel_layer.group_add(self.group_name, self.channel_name)

    async def disconnect(self, close_code):
        device = await self.get_device(self.device_id)
        if device:
            device.connection_status = False
            print(f"🔴 Device {self.device_id} disconnected")
            await self.save_device(device)

        # Remove from the WebSocket group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """Handle messages from the device"""
        data = json.loads(text_data)
        command = data.get("command")

        if command == "capture_image":
            print(f"📸 Received capture command from {self.device_id}")
            await self.send(text_data=json.dumps({"action": "capture"}))

    async def send_command(self, event):
        """Send command to the device"""
        command = event["command"]
        print(f"📢 Sending command '{command}' to device {self.device_id}")
        await self.send(text_data=json.dumps({"command": command}))

    async def get_or_create_device(self, device_id):
        from agriculture.models import Device  
        return await Device.objects.aget_or_create(device_id=device_id)

    async def get_device(self, device_id):
        from agriculture.models import Device  
        return await Device.objects.filter(device_id=device_id).afirst()

    async def save_device(self, device):
        await sync_to_async(device.save, thread_sensitive=True)()