from django.db import models
import json

class Device(models.Model):
    device_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    connection_status = models.BooleanField(default=False)
    last_connected = models.DateTimeField(auto_now=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    logs = models.TextField(default="[]")  # Store logs as a JSON list

    async def add_log(self, new_log):
        """Add a log entry and keep only the last 10 logs."""
        logs_list = json.loads(self.logs)  # Convert string to list
        logs_list.append(new_log)  # Add new log
        logs_list = logs_list[-10:]  # Keep only the last 10 logs
        self.logs = json.dumps(logs_list)  # Convert list back to string
        await self.save()

    def get_logs(self):
        """Return the last stored logs."""
        return json.loads(self.logs)  # Convert string back to list

    def __str__(self):
        return f"{self.device_id} - {'Online' if self.connection_status else 'Offline'}"

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