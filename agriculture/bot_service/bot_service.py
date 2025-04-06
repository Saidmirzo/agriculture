
from agriculture.models import BotUser
from requests import post


token = "7519067417:AAFjR06IiAzlhkuAkFti3YFMCVoq3pV_xFM"
def send_image_to_all(image_path):

    url = f"https://api.telegram.org/bot{token}/sendPhoto"

    with open(image_path, "rb") as image:
        for user in BotUser.objects.all():
            files = {'photo': image}
            data = {
                'chat_id': user.user_id,
                'caption': f"📸 Привет, {user.name}!"
            }
            resp = post(url, data=data, files=files)
            print(f"Sent to {user.name}, status: {resp.status_code}, text: {resp.text}")
            image.seek(0)  # Обязательно, иначе второй раз файл будет пустой


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