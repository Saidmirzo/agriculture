import asyncio
import json
import os
import sys
from pathlib import Path

# 1. 'client_bot' papkasidan bitta yuqoridagi asosiy loyiha papkasini topamiz
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# 2. Asosiy papka ichidan settings.py fayli qaysi papkada turganini avtomatik qidiramiz
settings_module = None
for path in BASE_DIR.glob("**/settings.py"):
    # venv yoki virtualenv ichidagi settings.py larni hisobga olmaymiz
    if "venv" not in path.parts and ".venv" not in path.parts:
        # Masalan: 'agriculture.settings' yoki 'config.settings' ko'rinishiga keltiramiz
        relative_path = path.relative_to(BASE_DIR).with_suffix("")
        settings_module = ".".join(relative_path.parts)
        break

if not settings_module:
    raise FileNotFoundError(
        "❌ settings.py fayli topilmadi! Loyihangiz ichida settings.py borligini tekshiring."
    )

# 3. Topilgan settings manzilini o'rnatamiz va Djangoni ishga tushiramiz
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

import django
django.setup()

# --- QOLGAN IMPORTLAR SHUNDAN KEYIN BOSHLANADI ---
from aiogram import Bot, Dispatcher, types
# ... qolgan kodlaringiz o'zgarishsiz qoladi ...
# ---------------------------------------------------------

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
from django.utils import timezone

from agriculture.models import BotUser, Device

token = "7519067417:AAFjR06IiAzlhkuAkFti3YFMCVoq3pV_xFM"

# Aiogram 3.x da HTML parse_mode mana shunday yoziladi
bot = Bot(token=token, default={"parse_mode": "HTML"})
dp = Dispatcher()
channel_layer = get_channel_layer()

USERS_FILE = Path(__file__).resolve().parent / "users.json"
active_intervals: dict[str, asyncio.Task] = {}


def load_allowed_users() -> list[int]:
    if not USERS_FILE.exists():
        USERS_FILE.write_text("[]", encoding="utf-8")

    try:
        data = json.loads(USERS_FILE.read_text(encoding="utf-8"))
        return [int(item) for item in data if isinstance(item, (int, str))]
    except json.JSONDecodeError:
        return []


def save_allowed_users(user_ids: list[int]) -> None:
    USERS_FILE.write_text(json.dumps([int(item) for item in user_ids], indent=2), encoding="utf-8")


def build_device_keyboard(devices: list[Device]) -> InlineKeyboardMarkup:
    keyboard = []
    for device in devices:
        title = f"{device.name} ({device.device_id})" if device.name else device.device_id
        status = "online" if device.connection_status else "offline"
        keyboard.append([
            InlineKeyboardButton(text=f"{title} — {status}", callback_data=f"select_device:{device.device_id}")
        ])
    keyboard.append([
        InlineKeyboardButton(text="🔄 Yangilash", callback_data="refresh_devices")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def build_device_control_keyboard(device_id: str) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="📸 Suratga olish", callback_data=f"command:{device_id}:capture"),
            InlineKeyboardButton(text="📍 Joylashuv", callback_data=f"command:{device_id}:location"),
        ],
        [
            InlineKeyboardButton(text="⚙️ Yangilash", callback_data=f"command:{device_id}:update"),
        ],
        [
            InlineKeyboardButton(text="⏱️ 10s interval", callback_data=f"interval:{device_id}:10"),
            InlineKeyboardButton(text="⏱️ 30s interval", callback_data=f"interval:{device_id}:30"),
        ],
        [
            InlineKeyboardButton(text="⏱️ 60s interval", callback_data=f"interval:{device_id}:60"),
            InlineKeyboardButton(text="⛔ Intervalni to‘xtatish", callback_data=f"stop_interval:{device_id}"),
        ],
        [
            InlineKeyboardButton(text="🔁 Qurilmalarni qayta ko‘rsatish", callback_data="refresh_devices"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def is_authorized(chat_id: int) -> bool:
    return chat_id in load_allowed_users()


async def authorize_user(chat_id: int, user_name: str) -> bool:
    if not is_authorized(chat_id):
        return False
    await sync_to_async(BotUser.objects.get_or_create)(user_id=chat_id, defaults={"name": user_name})
    return True


async def get_devices() -> list[Device]:
    return await sync_to_async(list)(Device.objects.all())


async def send_device_command(device_id: str, command: str, command_string: str = "") -> bool:
    device = await sync_to_async(Device.objects.filter(device_id=device_id, connection_status=True).first)()
    if not device:
        return False

    event = {"type": "send_command", "command": command, "command_string": command_string}
    await channel_layer.group_send(f"device_{device_id}", event)
    return True


async def stop_interval(device_id: str) -> bool:
    task = active_intervals.get(device_id)
    if task is None or task.done():
        return False
    task.cancel()
    active_intervals.pop(device_id, None)
    return True


async def interval_capture_loop(device_id: str, interval_seconds: int, chat_id: int) -> None:
    while True:
        success = await send_device_command(device_id, "capture", "")
        if not success:
            await bot.send_message(chat_id, f"❌ {device_id} uchun qurilma ulanmagan. Interval to‘xtatildi.")
            active_intervals.pop(device_id, None)
            break
        await bot.send_message(chat_id, f"⏱️ <b>{device_id}</b> ga suratga olish buyrug‘i yuborildi. Keyingi {interval_seconds}s da.")
        await asyncio.sleep(interval_seconds)


async def send_device_list(chat_id: int, text: str) -> None:
    devices = await get_devices()
    if not devices:
        await bot.send_message(chat_id, "📌 Bazada hozircha qurilma yo‘q.")
        return
    keyboard = build_device_keyboard(devices)
    await bot.send_message(chat_id, text, reply_markup=keyboard)


# Aiogram 3.x da komandalar Command() filtri orqali ushlanadi
@dp.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    if not await authorize_user(message.chat.id, message.from_user.full_name or "Anon"):
        await message.answer("❌ Sizda ruxsat yo‘q.")
        return
    await send_device_list(message.chat.id, "✅ Xush kelibsiz! Qurilmani tanlang:")


@dp.message(Command("devices"))
async def cmd_devices(message: types.Message) -> None:
    if not is_authorized(message.chat.id):
        await message.answer("❌ Sizda ruxsat yo‘q.")
        return
    await send_device_list(message.chat.id, "📱 Qurilmalar ro‘yxati:")


@dp.message(Command("help"))
async def cmd_help(message: types.Message) -> None:
    await message.answer(
        "📌 /start — boshlash\n"
        "/devices — qurilmalar ro‘yxatini ko‘rsatish\n"
        "Bot `client_bot/users.json` faylidagi IDlar bilan ishlaydi."
    )


@dp.callback_query()
async def callback_handler(callback_query: types.CallbackQuery) -> None:
    data = callback_query.data or ""
    chat_id = callback_query.message.chat.id
    await callback_query.answer()

    if not is_authorized(chat_id):
        await callback_query.message.answer("❌ Sizda ruxsat yo‘q.")
        return

    if data == "refresh_devices":
        await send_device_list(chat_id, "📱 Qurilmalar ro‘yxati:")
        return

    if data.startswith("select_device:"):
        device_id = data.split(":", 1)[1]
        await callback_query.message.edit_text(
            f"✅ <b>{device_id}</b> tanlandi. Endi buyruqni tanlang:",
            reply_markup=build_device_control_keyboard(device_id),
        )
        return

    if data.startswith("command:"):
        _, device_id, command_key = data.split(":", 2)
        command_map = {
            "capture": "capture",
            "location": "location",
            "update": "update",
        }
        command = command_map.get(command_key)
        if not command:
            await callback_query.message.answer("❌ Noto‘g‘ri buyruq.")
            return
        if await send_device_command(device_id, command):
            await callback_query.message.answer(f"✅ {device_id} ga <b>{command}</b> buyrug‘i yuborildi.")
        else:
            await callback_query.message.answer(f"❌ {device_id} qurilmasi hozir ulanmagan.")
        return

    if data.startswith("interval:"):
        _, device_id, interval_value = data.split(":", 2)
        try:
            interval_seconds = int(interval_value)
        except ValueError:
            await callback_query.message.answer("❌ Interval qiymati noto‘g‘ri.")
            return
        if device_id in active_intervals:
            await stop_interval(device_id)
        task = asyncio.create_task(interval_capture_loop(device_id, interval_seconds, chat_id))
        active_intervals[device_id] = task
        await callback_query.message.answer(f"⏱️ {device_id} uchun {interval_seconds}s intervaldagi suratga olish boshlandi.")
        return

    if data.startswith("stop_interval:"):
        device_id = data.split(":", 1)[1]
        if await stop_interval(device_id):
            await callback_query.message.answer(f"🛑 {device_id} uchun interval to‘xtatildi.")
        else:
            await callback_query.message.answer(f"ℹ️ {device_id} uchun interval faol emas.")
        return

    await callback_query.message.answer("❌ Noma’lum callback bayt.")


@dp.message()
async def catch_all(message: types.Message) -> None:
    await message.answer(
        "⚠️ Iltimos /start tugmasini bosing yoki /devices bilan qurilmalarni ko‘ring."
    )


async def main() -> None:
    print("🚀 Telegram client bot boshlandi...")
    # Aiogram 3.x uchun to'g'ri polling start qilish usuli
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("🤖 Bot to'xtatildi.")