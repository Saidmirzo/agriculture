import json
from channels.generic.websocket import AsyncWebsocketConsumer

class DeviceLogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Connect to WebSocket and join group"""
        await self.channel_layer.group_add("device_logs_group", self.channel_name)
        await self.accept()
        print("✅ WebSocket Connected")

    async def disconnect(self, close_code):
        """Leave WebSocket group on disconnect"""
        await self.channel_layer.group_discard("device_logs_group", self.channel_name)
        print("❌ WebSocket Disconnected")

    async def send_data(self, event):
        """Send real-time data updates to frontend"""
        message = event["message"]
        await self.send(text_data=message)