
from agriculture.models import BotUser
from requests import post


token = "7519067417:AAFjR06IiAzlhkuAkFti3YFMCVoq3pV_xFM"




import requests
import logging

# !!! BU YERGA O'ZINGIZNING TELEGRAM ID'INGIZNI YOZING (MASALAN: 12345678)
ADMIN_CHAT_ID = "1963680139" 

def send_error_to_admin(error_message):
    """Xatolik yuz berganda adminga bot orqali xabar yuborish funksiyasi"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        'chat_id': ADMIN_CHAT_ID,
        'text': f"🚨 **[SERVER OGOHLANTIRISHI]**\n\nMuammo: {error_message}",
        'parse_mode': 'Markdown'
    }
    try:
        # Adminga xabar yuborishda ham timeout qo'yamiz, server qotib qolmasligi uchun
        requests.post(url, data=data, timeout=5)
    except Exception:
        pass


def send_image_to_all(image_path):
    url_photo = f"https://api.telegram.org/bot{token}/sendPhoto"
    url_file = f"https://api.telegram.org/bot{token}/sendDocument"

    with open(image_path, "rb") as image:
        for user in BotUser.objects.all():
            try:
                caption = f"📸 Привет, {user.name}!"
                files = {'photo': image}
                data = {'chat_id': user.user_id, 'caption': caption}
                
                resp = requests.post(url_photo, data=data, files=files, timeout=5)

                if resp.status_code != 200:
                    image.seek(0)
                    files = {'document': image}
                    data = {'chat_id': user.user_id, 'caption': f"📎 Привет, {user.name} (файл вместо фото)!"}
                    resp = requests.post(url_file, data=data, files=files, timeout=5)

                print(f"Sent to {user.name}, status: {resp.status_code}")

            except requests.exceptions.RequestException as e:
                # ❗️ Xatolikni ushlab, adminga bot orqali yuboramiz
                error_msg = f"Rasm yuborishda ulanish xatosi (User: {user.name}).\nDetallar: {repr(e)}"
                print(f"[TIMEOUT/NETWORK ERROR] {error_msg}")
                send_error_to_admin(error_msg)
                
            except Exception as e:
                error_msg = f"Rasm yuborishda kutilmagan xato (User: {user.name}).\nDetallar: {repr(e)}"
                print(f"[ERROR] {error_msg}")
                send_error_to_admin(error_msg)
            finally:
                image.seek(0)


def send_location_to_users(latitude, longitude):
    url = f"https://api.telegram.org/bot{token}/sendLocation"

    for user in BotUser.objects.all():
        data = {
            'chat_id': user.user_id,
            'latitude': latitude,
            'longitude': longitude
        }
        try:
            response = requests.post(url, data=data, timeout=5)

            if response.status_code != 200:
                error_msg = f"Lokatsiya yuborilmadi (User: {user.name}). Status: {response.status_code}, Text: {response.text}"
                print(f"❌ {error_msg}")
                send_error_to_admin(error_msg)
            else:
                print(f"✅ Локация отправлена {user.name}")
                
        except requests.exceptions.RequestException as e:
            # ❗️ Tarmoq yoki Timeout xatosi bo'lsa adminga yuboramiz
            error_msg = f"Lokatsiya yuborishda ulanish xatosi (User: {user.name}).\nDetallar: {repr(e)}"
            print(f"⚠️ {error_msg}")
            send_error_to_admin(error_msg)

# import requests
# import logging

# def send_image_to_all(image_path):
#     url_photo = f"https://api.telegram.org/bot{token}/sendPhoto"
#     url_file = f"https://api.telegram.org/bot{token}/sendDocument"

#     with open(image_path, "rb") as image:
#         for user in BotUser.objects.all():
#             try:
#                 caption = f"📸 Привет, {user.name}!"
#                 files = {'photo': image}
#                 data = {'chat_id': user.user_id, 'caption': caption}
                
#                 # Majburiy timeout=5 qo'shildi (5 soniyadan ko'p kutmaydi)
#                 resp = requests.post(url_photo, data=data, files=files, timeout=5)

#                 if resp.status_code != 200:
#                     image.seek(0)
#                     files = {'document': image}
#                     data = {'chat_id': user.user_id, 'caption': f"📎 Привет, {user.name} (файл вместо фото)!"}
#                     resp = requests.post(url_file, data=data, files=files, timeout=5)

#                 print(f"Sent to {user.name}, status: {resp.status_code}")

#             except requests.exceptions.RequestException as e:
#                 # Telegramga ulanishda muammo bo'lsa, server qotmaydi, keyingi userga o'tadi
#                 print(f"[TIMEOUT/NETWORK ERROR] Telegram ulanmadi: {repr(e)}")
#             except Exception as e:
#                 print(f"[ERROR] Boshqa xatolik {repr(e)}")
#             finally:
#                 # Har qanday holatda ham fayl ko'rsatkichini boshiga qaytaramiz
#                 image.seek(0)

# def send_image_to_all(image_path):
#     url_photo = f"https://api.telegram.org/bot{token}/sendPhoto"
#     url_file = f"https://api.telegram.org/bot{token}/sendDocument"

#     with open(image_path, "rb") as image:
#         for user in BotUser.objects.all():
#             files = {'photo': image}
#             data = {
#                 'chat_id': user.user_id,
#                 'caption': f" Привет, {user.name}!"
#             }
#             resp = post(url_photo, data=data, files=files)

#             if resp.status_code != 200:
#                 print(f"[WARNING] Photo failed for {user.name}, trying as document...")
#                 files = {'document': image}
#                 data = {
#                     'chat_id': user.user_id,
#                     'caption': f"📎 Привет, {user.name} (файл вместо фото)!"
#                 }
#                 response = post(url_file, data=data, files=files)

#             print(f"Sent to {user.name}, status: {resp.status_code}, text: {resp.text}")
#             image.seek(0)  # Обязательно, иначе второй раз файл будет пустой



    # for user in BotUser.objects.all():
    #     with open(image_path, "rb") as image:
    #         files = {'photo': image}
    #         data = {
    #             'chat_id': user.user_id,
    #             'caption': f"📸 Привет, {user.name}!"
    #         }

    #         print(f"Sending photo to {user.name}...")
    #         response = post(url_photo, data=data, files=files)

    #     # If failed — try as document
    #     if response.status_code != 200:
    #         print(f"[WARNING] Photo failed for {user.name}, trying as document...")

    #         with open(image_path, "rb") as image_file:
    #             files = {'document': image_file}
    #             data = {
    #                 'chat_id': user.user_id,
    #                 'caption': f"📎 Привет, {user.name} (файл вместо фото)!"
    #             }
    #             response = post(url_file, data=data, files=files)

    #     print(f"[INFO] Sent to {user.name}, status: {response.status_code}, response: {response.text}")


# def send_location_to_users(latitude, longitude):
#     url = f"https://api.telegram.org/bot{token}/sendLocation"

#     for user in BotUser.objects.all():
#         data = {
#             'chat_id': user.user_id,
#             'latitude': latitude,
#             'longitude': longitude
#         }
#         response = post(url, data=data)

#         if response.status_code != 200:
#             print(f"❌ Не удалось отправить локацию пользователю {user.name}: {response.text}")