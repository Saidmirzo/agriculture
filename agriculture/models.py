from django.db import models


class Device(models.Model):
    device_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    connection_status = models.BooleanField(default=False)
    last_connected = models.DateTimeField(auto_now=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

class DeviceData(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='data')
    data_type = models.CharField(max_length=50)  # e.g., "location", "image"
    data_value = models.TextField(blank=True, null=True)  # JSON or metadata
    file = models.FileField(upload_to='device_files/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)



class DeviceImage(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="images")
    image_path = models.CharField(max_length=500)  # Store only the path
    timestamp = models.DateTimeField(auto_now_add=True)