
#!/bin/bash

sudo systemctl restart daphne_agriculture
sudo systemctl restart gunicorn_agriculture
# Ranglar (Konsolda chiroyli ko'rinishi uchun)
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # Rangni qayta tiklash

echo -e "${BLUE}🔄 Qayta yuklash jarayoni boshlandi...${NC}"
echo "----------------------------------------"

# 1. Telegram bot xizmatini qayta start qilish
echo "1. Telegram Botni qayta yuklash..."
sudo systemctl restart tgbot.service

# 2. Django Channels / ASGI (Daphne) xizmatini qayta start qilish
# Eslatma: Agar daphne xizmati nomi boshqacha bo'lsa (masalan: daphne.service), o'zgartirib qo'ying
if systemctl list-units --full -all | grep -q "daphne.service"; then
    echo "2. Daphne (ASGI) xizmatini qayta yuklash..."
    sudo systemctl restart daphne.service
fi

# 3. Nginx veb-serverini qayta start qilish
echo "3. Nginx veb-serverini qayta yuklash..."
sudo systemctl restart nginx

echo "----------------------------------------"
echo -e "${GREEN}✅ Barcha xizmatlar muvaffaqiyatli qayta yuklandi!${NC}"
echo "----------------------------------------"

# Xizmatlarning hozirgi holatini qisqacha ko'rsatish
echo -e "${BLUE}📊 Xizmatlar holati:${NC}"
sudo systemctl status tgbot.service | grep -E "Active:|Main PID:"
if systemctl list-units --full -all | grep -q "daphne.service"; then
    sudo systemctl status daphne.service | grep -E "Active:|Main PID:"
fi
sudo systemctl status nginx | grep -E "Active:|Main PID:"