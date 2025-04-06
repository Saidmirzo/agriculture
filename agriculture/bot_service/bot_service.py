
from agriculture.models import BotUser
from requests import post


token = "7519067417:AAFjR06IiAzlhkuAkFti3YFMCVoq3pV_xFM"

def send_image_to_all(image_path):
    url_photo = f"https://api.telegram.org/bot{token}/sendPhoto"
    url_file = f"https://api.telegram.org/bot{token}/sendDocument"

    for user in BotUser.objects.all():
        with open(image_path, "rb") as image:
            files = {'photo': image}
            data = {
                'chat_id': user.user_id,
                'caption': f"📸 Привет, {user.name}!"
            }

            print(f"Sending photo to {user.name}...")
            response = post(url_photo, data=data, files=files)

        # If failed — try as document
        if response.status_code != 200:
            print(f"[WARNING] Photo failed for {user.name}, trying as document...")

            with open(image_path, "rb") as image_file:
                files = {'document': image_file}
                data = {
                    'chat_id': user.user_id,
                    'caption': f"📎 Привет, {user.name} (файл вместо фото)!"
                }
                response = post(url_file, data=data, files=files)

        print(f"[INFO] Sent to {user.name}, status: {response.status_code}, response: {response.text}")


def send_location_to_users(latitude, longitude):
    url = f"https://api.telegram.org/bot{token}/sendLocation"

    for user in BotUser.objects.all():
        data = {
            'chat_id': user.user_id,
            'latitude': latitude,
            'longitude': longitude
        }
        response = post(url, data=data)

        if response.status_code != 200:
            print(f"❌ Не удалось отправить локацию пользователю {user.name}: {response.text}")