# import paho.mqtt.client as mqtt
# import json
# from django.utils.timezone import now

# from core.settings import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC_PREFIX

# from .models import Device, DeviceData



# def on_connect(client, userdata, flags, rc):
#     print("Connected to MQTT Broker")
#     client.subscribe(f"{MQTT_TOPIC_PREFIX}#")  # Subscribe to all device topics

# def on_message(client, userdata, msg):
#     try:
#         payload = json.loads(msg.payload.decode())
#         topic_parts = msg.topic.split("/")
#         device_id = topic_parts[1]

#         # Get or create the device
#         device, _ = Device.objects.get_or_create(device_id=device_id)

#         # Handle specific topics
#         if topic_parts[-1] == "status":
#             device.connection_status = payload.get("status") == "connected"
#             device.save()
#         elif topic_parts[-1] == "location":
#             DeviceData.objects.create(
#                 device=device,
#                 data_type="location",
#                 data_value=json.dumps(payload),
#             )
#         elif topic_parts[-1] == "image":
#             # Save metadata about the image
#             DeviceData.objects.create(
#                 device=device,
#                 data_type="image",
#                 data_value=json.dumps({"description": payload.get("description")}),
#             )
#     except Exception as e:
#         print("Error processing message:", e)

# # MQTT Client Setup
# client = mqtt.Client()
# client.on_connect = on_connect
# client.on_message = on_message
# client.connect(MQTT_BROKER, MQTT_PORT, 60)

# # Run the MQTT client loop in a thread

# def start_mqtt_client():
#     client.connect(MQTT_BROKER, MQTT_PORT, 60)
#     client.loop_start() 
# # import threading
# # mqtt_thread = threading.Thread(target=client.loop_forever)
# # mqtt_thread.start()
