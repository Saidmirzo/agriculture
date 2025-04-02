from django.contrib import admin

from django.contrib import admin
from .models import Device, DeviceImage, DeviceData, DeviceLog, BotUser

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("device_id", "connection_status", "last_connected")

@admin.register(DeviceImage)
class DeviceImageAdmin(admin.ModelAdmin):
    list_display = ("device", "image_path", "timestamp")

@admin.register(DeviceData)
class DeviceDataAdmin(admin.ModelAdmin):
    list_display = ("device", "data_type", "data_value", "created_at")

@admin.register(DeviceLog)
class DeviceDataAdmin(admin.ModelAdmin):
    pass


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'name', 'created_at')
    search_fields = ('user_id', 'name')