import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now
from asgiref.sync import sync_to_async
from django.db import transaction

class DeviceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.device_id = self.scope["url_route"]["kwargs"]["device_id"]
        self.group_name = f"device_{self.device_id}"  # Har bir qurilma o'z guruhiga ega

        # 1-QADAM: Avval guruhga qo'shish (Redis ulanishini birinchi navbatda hal qilamiz)
        print(f"[INFO] Adding device {self.device_id} to group: {self.group_name}")
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        
        # 2-QADAM: Handshake'ni yakunlash (Ulanishni qabul qilish)
        await self.accept()

        # 3-QADAM: Baza bilan ishlashni ulanish tugagandan keyinga qoldiramiz
        try:
            device, created = await self.get_or_create_device(self.device_id)
            device.connection_status = True
            device.last_connected = now()
            await self.save_device(device)
        except Exception as e:
            print(f"[ERROR] Failed to update device status on connect: {e}")

    async def disconnect(self, close_code):
        try:
            device = await self.get_device(self.device_id)
            if device:
                device.connection_status = False
                print(f"[WARNING] Device {self.device_id} disconnected")
                await self.save_device(device)
            else:
                print(f"[WARNING] Device {self.device_id} disconnect called but device record not found")
        except Exception as exc:
            print(f"[ERROR] Failed to update device {self.device_id} status on disconnect: {exc}")
        finally:
            # Guruhdan o'chirish har doim blokda bo'lishi shart
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """Device'dan kelgan xabarlarni qayta ishlash"""
        try:
            data = json.loads(text_data)
            await self.save_log(data)
        except json.JSONDecodeError:
            print(f"[ERROR] Invalid JSON received from {self.device_id}")
        except Exception as e:
            print(f"[ERROR] Error in receive: {e}")

    async def send_command(self, event):
        """Device'ga buyruq yuborish"""
        command = event["command"]
        command_string = event["command_string"]
        print(f"[INFO] Sending command '{command}' to device {self.device_id}")
        await self.send(text_data=json.dumps({"command": command, "command_string": command_string}))

    # ---- BAZA BILAN ISHLASH METODLARI (OPTIMALLASHGAN) ----

    async def get_or_create_device(self, device_id):
        from agriculture.models import Device  
        return await Device.objects.aget_or_create(device_id=device_id)

    async def get_device(self, device_id):
        from agriculture.models import Device  
        return await Device.objects.filter(device_id=device_id).afirst()

    async def save_device(self, device):
        # Asinxron saqlash uchun xavfsiz usul
        await sync_to_async(device.save, thread_sensitive=True)()

    async def save_log(self, response):
        from agriculture.models import Device, DeviceLog

        # 1) Device’ni asinxron topish (aget ishlatamiz, sync_to_async shartmas)
        try:
            device = await Device.objects.aget(device_id=self.device_id)
        except Device.DoesNotExist:
            print(f"[ERROR] Device {self.device_id} not found for logging")
            return

        # 2) Loglarni ro'yxatga normallashtirish
        data = response.get("logs")
        logs = data if isinstance(data, list) else [data]
        logs = [l for l in logs if l is not None]
        if not logs:
            return

        # 3) Yangi loglarni qo‘shish (bulk_create)
        def _bulk_create():
            DeviceLog.objects.bulk_create(
                [DeviceLog(device=device, log=log) for log in logs]
            )
        await sync_to_async(_bulk_create, thread_sensitive=True)()

        # 4) Prune (Eski loglarni o'chirish)
        limit = 2
        await sync_to_async(prune_device_logs, thread_sensitive=True)(device, limit)


# Tranzaksiya bilan ishlovchi funksiya consumer'dan tashqarida qoladi
def prune_device_logs(device, limit: int):
    from agriculture.models import DeviceLog
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