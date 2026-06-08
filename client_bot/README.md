# Agriculture Client Bot

Bu katalog Telegram bot uchun oddiy klientni o‘z ichiga oladi. Bot `agriculture.bot_service.bot_service` ichidagi `token` dan foydalanadi.

## Foydalanish

1. `agriculture/client_bot/users.json` fayliga ruxsat berilgan Telegram foydalanuvchi IDlarini qo‘shing, masalan:

```json
[123456789, 987654321]
```

2. Django loyihasi asosiy papkasida quyidagicha ishga tushiring:

```bash
python manage.py run_client_bot
```

3. Telegramda botga `/start` yozing.

## Bot ishlashi

- `/start` bosilganda foydalanuvchi IDsi `client_bot/users.json` dan tekshiriladi.
- Agar ruxsat bo‘lsa, bazadagi qurilmalar inline tugmalar ko‘rinishida yuboriladi.
- Qurilma tanlangach, bot qurilma uchun buyruqlarni yuboradi:
  - suratga olish
  - joylashuv yuborish
  - 10s/30s/60s intervalda suratga olish
  - intervalni to‘xtatish
  - yangilash

## Eslatma

Bot `channels_redis` orqali `device_<device_id>` guruhiga `send_command` voqeasini yuboradi. Qurilma tomoni `agriculture/device/consumers.py` dagi `send_command` metodiga mos kelishi kerak.
