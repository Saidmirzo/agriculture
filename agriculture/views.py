from http import client
import os

from rest_framework.generics import GenericAPIView, CreateAPIView, ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from agriculture.serializers import DeviceCreateSerializer, SendEventSerializer, UploadImageSerializer

from .models import Device, DeviceImage, DeviceData

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class DeviceStatusView(APIView):
    def get(self, request):
        devices = Device.objects.values("device_id", "connection_status", "last_connected")
        return Response(devices)


class TriggerEventView(ListCreateAPIView):
    serializer_class = DeviceCreateSerializer 
    queryset = Device.objects.all()
    


class DeviceDataView(APIView):
    def get(self, request, device_id):
        data = DeviceData.objects.filter(device__device_id=device_id).values(
            "data_type", "data_value", "created_at"
        )
        return Response(data)





class UploadImageView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = UploadImageSerializer
    def post(self, request, *args, **kwargs):
        device_id = request.data.get("device_id")
        image = request.FILES.get("image")  # Use FILES for image uploads

        if not device_id or not image:
            return Response({"error": "Missing device_id or image"}, status=400)

        # Check if the device exists
        device = Device.objects.filter(device_id=device_id).first()
        if not device:
            return Response({"error": "Device not found"}, status=400)

        # Define custom directory
        upload_dir = os.path.join("public", "images", device_id)
        os.makedirs(upload_dir, exist_ok=True)  # Create directory if it doesn't exist

        # Define image path
        image_path = os.path.join(upload_dir, image.name)
        relative_image_path = os.path.join("images", device_id, image.name)

        # Save image to disk
        with open(image_path, "wb+") as destination:
            for chunk in image.chunks():
                destination.write(chunk)

        # Save only the image path in the database
        device_image = DeviceImage.objects.create(device=device, image_path=relative_image_path)

        return Response({"message": "Image uploaded successfully", "image_path": relative_image_path}, status=200)


class UpdateLocationView(APIView):

    def post(self, request, *args, **kwargs):
        device_id = request.data.get("device_id")
        latitude = request.data.get("latitude")
        longitude = request.data.get("longitude")

        if not device_id or latitude is None or longitude is None:
            return Response({"error": "Missing required parameters"}, status=status.HTTP_400_BAD_REQUEST)

        device = Device.objects.filter(device_id=device_id).first()
        if not device:
            return Response({"error": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

        # Update the device location
        device.latitude = latitude
        device.longitude = longitude
        device.save()

        return Response({"message": "Location updated successfully"}, status=status.HTTP_200_OK)




class SendEventView(CreateAPIView):
    serializer_class=SendEventSerializer
    def post(self, request, *args, **kwargs):
        device_id = request.data.get("device_id")
        command = request.data.get("command")

        if not device_id or not command:
            return Response({"error": "Missing device_id or command"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if device exists
        device = Device.objects.filter(device_id=device_id, connection_status=True).first()
        if not device:
            return Response({"error": "Device not connected"}, status=status.HTTP_404_NOT_FOUND)

        # Send WebSocket event to the specific device group
        channel_layer = get_channel_layer()
        group_name = f"device_{device_id}"
        
        print(f"📡 Sending command '{command}' to WebSocket group: {group_name}")

        async_to_sync(channel_layer.group_send)(
            group_name,
            {"type": "send_command", "command": command}
        )

        return Response({"message": f"Command '{command}' sent to device {device_id}"}, status=status.HTTP_200_OK)
    

class UploadLogsView(APIView):
    """API view for uploading logs from a device."""

    def post(self, request, *args, **kwargs):
        from agriculture.models import Device, DeviceLog
        device_id = request.data.get("device_id")
        logs = request.data.get("logs")

        if not device_id or not logs:
            return Response({"error": "Missing device_id or logs"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch device
        device = Device.objects.filter(device_id=device_id).first()
        if not device:
            return Response({"error": "Device not found"}, status=status.HTTP_404_NOT_FOUND)

        # Save logs as separate entries
        if isinstance(logs, list):  # Ensure logs are sent as a list
            for log in logs:
                DeviceLog.objects.create(device=device, log=log)
        else:
            DeviceLog.objects.create(device=device, log=str(logs))

        return Response({"message": "Logs updated successfully"}, status=status.HTTP_200_OK)
    

from django.shortcuts import render

def device_logs_view(request):
    """Render the real-time device logs page"""
    devices = Device.objects.prefetch_related("logs").all()
    return render(request, "device_logs.html", {"devices": devices})

def real_device_logs_view(request):
    devices = Device.objects.all()
    return render(request, "real_time_device_logs.html", {"devices": devices})

