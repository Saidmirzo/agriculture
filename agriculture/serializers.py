from rest_framework.serializers import ModelSerializer
from agriculture.models import Device
from rest_framework import serializers

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