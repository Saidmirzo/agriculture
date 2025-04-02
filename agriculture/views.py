from http import client
import os

from rest_framework.generics import GenericAPIView, CreateAPIView, ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from agriculture.bot_service.bot_service import send_image_to_all, send_location_to_users
from agriculture.serializers import DeviceCreateSerializer, SendEventSerializer, UploadImageSerializer, DeviceLogSerializer

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
        send_image_to_all(image_path)

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
        send_location_to_users(latitude, longitude)

        return Response({"message": "Location updated successfully"}, status=status.HTTP_200_OK)




class SendEventView(CreateAPIView):
    serializer_class=SendEventSerializer
    def post(self, request, *args, **kwargs):
        device_id = request.data.get("device_id")
        command = request.data.get("command")
        command_string = request.data.get("command_string")

        if not device_id or not command:
            return Response({"error": "Missing device_id or command"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if device exists
        device = Device.objects.filter(device_id=device_id, connection_status=True).first()
        if not device:
            return Response({"error": "Device not connected"}, status=status.HTTP_404_NOT_FOUND)

        # Send WebSocket event to the specific device group
        channel_layer = get_channel_layer()
        group_name = f"device_{device_id}"
        
        print(f"[SEND] Sending command '{command}' to WebSocket group: {group_name}")

        async_to_sync(channel_layer.group_send)(
            group_name,
            {"type": "send_command", "command": command, "command_string":command_string}
        )

        return Response({"message": f"Command '{command}' sent to device {device_id}"}, status=status.HTTP_200_OK)
    

class UploadLogsView(CreateAPIView):
    """API view for uploading logs from a device."""
    serializer_class=DeviceLogSerializer

    def post(self, request, *args, **kwargs):
        from agriculture.models import Device, DeviceLog
        serializer=DeviceLogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        device_id = serializer.validated_data.get('device_id')
        logs = serializer.validated_data.get('logs')


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
    from .models import Device
    """Render the real-time device logs page"""
    devices = Device.objects.prefetch_related("logs").all()
    context = {
        "devices": devices
    }
    return render(request, "device_logs.html", context)


def real_device_logs_view(request):
    devices = Device.objects.all()
    return render(request, "real_time_device_logs.html", {"devices": devices})


from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from .models import BotUser
import json


@method_decorator(csrf_exempt, name='dispatch')
class BotUserView(View):
    """
    POST — добавление пользователя
    DELETE — удаление пользователя
    """
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        user_id = data.get("user_id")
        name = data.get("name")

        if not user_id or not name:
            return JsonResponse({"error": "user_id and name required"}, status=400)

        user, created = BotUser.objects.get_or_create(user_id=user_id, defaults={"name": name})
        if not created:
            return JsonResponse({"message": "User already exists"}, status=200)

        return JsonResponse({"message": "User added"}, status=201)

    def delete(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        user_id = data.get("user_id")
        if not user_id:
            return JsonResponse({"error": "user_id required"}, status=400)

        deleted, _ = BotUser.objects.filter(user_id=user_id).delete()
        if deleted:
            return JsonResponse({"message": "User removed"}, status=200)
        else:
            return JsonResponse({"message": "User not found"}, status=404)