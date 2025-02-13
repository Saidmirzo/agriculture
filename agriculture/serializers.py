from rest_framework.serializers import ModelSerializer
from agriculture.models import Device
from rest_framework import serializers

from rest_framework import serializers
from agriculture.models import DeviceLog

class DeviceCreateSerializer(ModelSerializer):
    class Meta:
        model = Device
        fields = ['device_id', 'name', 'connection_status']
    


class DeviceDataSerializer(serializers.Serializer):
    device_id = serializers.CharField()

class UploadImageSerializer(serializers.Serializer):
    device_id = serializers.CharField()
    image = serializers.ImageField()

class UpdateLocationSerializer(serializers.Serializer):
    device_id = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

class SendEventSerializer(serializers.Serializer):
    device_id = serializers.CharField()
    command = serializers.CharField()

class DeviceLogSerializer(serializers.Serializer):
    """Serializer for Device Logs"""
    device_id = serializers.CharField()
    logs = serializers.CharField()


class DeviceLogModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceLog
        fields = ["timestamp", "log"]

class DeviceSerializer(serializers.ModelSerializer):
    logs = DeviceLogSerializer(many=True, read_only=True)

    class Meta:
        model = Device
        fields = ["device_id", "name", "connection_status", "last_connected", "latitude", "longitude", "logs"]
   