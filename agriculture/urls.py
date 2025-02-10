from django.urls import path

from .views import DeviceDataView, DeviceStatusView, SendEventView, TriggerEventView, UpdateLocationView, UploadImageView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

urlpatterns = [
    path('devices/status/', DeviceStatusView.as_view(), name='device-status'),
    path('devices/', TriggerEventView.as_view(), name='trigger-event'),
    path('devices/<str:device_id>/data/', DeviceDataView.as_view(), name='device-data'),
    path("update-location/", UpdateLocationView.as_view(), name="update_location"),
    path("send-event/", SendEventView.as_view(), name="send_event"),
    path("send-image/", UploadImageView.as_view(), name="send_image"),
    
]