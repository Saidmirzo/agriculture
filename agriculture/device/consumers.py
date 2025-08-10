import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now
from asgiref.sync import sync_to_async

from agriculture.models import Device, DeviceLog


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
        print(f"[INFO] Adding device {self.device_id} to group: {self.group_name}")
        await self.channel_layer.group_add(self.group_name, self.channel_name)

    async def disconnect(self, close_code):
        device = await self.get_device(self.device_id)
        if device:
            device.connection_status = False
            print(f"[WARNING] Device {self.device_id} disconnected")
            await self.save_device(device)

        # Remove from the WebSocket group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """Handle messages from the device"""
        data = json.loads(text_data)
        await self.save_log(data)

        # if command == "capture_image":
        #     print(f"[INFO] Received capture command from {self.device_id}")
        #     await self.send(text_data=json.dumps({"action": "capture"}))

    async def send_command(self, event):
        """Send command to the device"""
        command = event["command"]
        command_string = event["command_string"]
        print(f"[INFO] Sending command '{command}' to device {self.device_id}")
        await self.send(text_data=json.dumps({"command": command, "command_string":command_string}))

    async def get_or_create_device(self, device_id):
        from agriculture.models import Device  
        return await Device.objects.aget_or_create(device_id=device_id)

    async def get_device(self, device_id):
        from agriculture.models import Device  
        return await Device.objects.filter(device_id=device_id).afirst()

    async def save_device(self, device):
        await sync_to_async(device.save, thread_sensitive=True)()

    async def save_log(self, response):
        # 1) Device’ni topish
        device = await sync_to_async(Device.objects.get)(device_id=self.device_id)

        # 2) Loglarni listga normallashtirish
        data = response.get("logs")
        logs = data if isinstance(data, list) else [data]
        logs = [l for l in logs if l is not None]  # None bo‘lsa tashlab yuboramiz
        if not logs:
            return

        # 3) Yangi loglarni qo‘shish (bulk_create)
        await sync_to_async(DeviceLog.objects.bulk_create)(
            [DeviceLog(device=device, log=log) for log in logs]
        )

        # 4) Prune (faqat oxirgi N ta logni qoldirish)
        limit = 2
        await sync_to_async(prune_device_logs)(device, limit)

from django.db import transaction

def prune_device_logs(device, limit: int):
    """
    Faqat eng so‘nggi `limit` ta logni qoldiradi, qolganlarini o‘chiradi.
    """
    with transaction.atomic():
        keep_ids = list(
            DeviceLog.objects
            .filter(device=device)
            .order_by('-timestamp')
            .values_list('id', flat=True)[:limit]
        )
        if keep_ids:
            DeviceLog.objects.filter(device=device).exclude(id__in=keep_ids).delete()

    

