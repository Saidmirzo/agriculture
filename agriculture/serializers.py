from rest_framework.serializers import ModelSerializer
from agriculture.models import Device, DeviceImage
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
    command_string = serializers.CharField()

class DeviceLogSerializer(serializers.Serializer):
    """Serializer for Device Logs"""
    device_id = serializers.CharField()
    log = serializers.CharField()
    timestamp = serializers.DateTimeField()


class DeviceLogModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceLog
        fields = ["timestamp", "log"]

class DeviceSerializer(serializers.ModelSerializer):
    logs = DeviceLogSerializer(many=True, read_only=True)

    class Meta:
        model = Device
        fields = ["device_id", "name", "connection_status", "last_connected", "latitude", "longitude", "logs"]
   

from django.conf import settings
from urllib.parse import urljoin
class DeviceImageSerializer(serializers.ModelSerializer):
    full_image_url = serializers.SerializerMethodField()

    class Meta:
        model = DeviceImage
        fields = '__all__'

    def get_full_image_url(self, obj):
        request = self.context.get('request')
        if request is not None:
            media_url = request.build_absolute_uri(settings.MEDIA_URL)
            return urljoin(media_url, obj.image_path)
        return settings.MEDIA_URL + obj.image_path

class DeviceImagesSerializer(serializers.ModelSerializer):
    data = DeviceDataSerializer(many=True, read_only=True)
    images = DeviceImageSerializer(many=True, read_only=True)

    class Meta:
        model = Device
        fields = [
            'device_id',
            'name',
            'connection_status',
            'last_connected',
            'latitude',
            'longitude',
            'data',
            'images',
        ]