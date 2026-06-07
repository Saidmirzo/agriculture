# Agriculture Backend Deployment Guide (O'zbek)

## 📋 Ro'yxatga olish va Tayyorlash

### 1. Server tayyorlash
```bash
# SSH orqali serverga kirish
ssh root@your-server-ip

# Working directory ga kirish
cd ~
```

### 2. Repository clone qilish
```bash
git clone https://github.com/Saidmirzo/agriculture.git
cd agriculture
```

### 3. Deployment script o'quvchi qilish va ishga tushirish
```bash
# Script qilish (executable)
chmod +x deploy.sh
chmod +x manage-services.sh
chmod +x setup-ssl.sh
chmod +x update-deploy.sh

# Deployment ishga tushirish (bu 5-10 minut davom etadi)
sudo ./deploy.sh
```

---

## 📝 Script Tavsifi

### `deploy.sh` - Asosiy Deploy Script
Birinchi marta ishga tushuriladi. Quyidagilarni qiladi:

✅ System packages o'rnatish (nginx, postgresql, redis, python3, etc.)
✅ PostgreSQL database yaratish  
✅ Redis server sozlash
✅ Python virtual environment yaratish
✅ Django packages o'rnatish
✅ `.env` fayl sozlash
✅ Django migrations qilish
✅ Gunicorn (HTTP API server) sozlash
✅ Daphne (WebSocket/ASGI server) sozlash
✅ Nginx reverse proxy sozlash
✅ SSL sertifikat sozlash (Let's Encrypt)
✅ Systemd services yaratish va ishga tushirish
✅ Firewall sozlash

**Ishga tushirish:**
```bash
sudo ./deploy.sh
```

**Chiqarish:**
- Database credentials faylda saqlanadi: `/var/www/agriculture/DATABASE_CREDENTIALS.txt`
- Nginx, Gunicorn, Daphne, PostgreSQL, Redis avtomatik ishga tushadi

---

### `manage-services.sh` - Service Management
Services statussini ko'rish, restart qilish, logs ko'rish, backup qilish uchun menu.

**Ishga tushirish:**
```bash
./manage-services.sh
```

**Menyu options:**
1. Services status ko'rish
2. Services qayta ishga tushirish  
3. Git pull (update)
4. Django migrations
5. Static files collect
6. Gunicorn logs
7. Daphne logs
8. Nginx logs
9. Redis test
10. Database backup
11. Services stop
12. Services start
13. SSH key qo'shish

---

### `setup-ssl.sh` - SSL Setup Script
Let's Encrypt orqali HTTPS sertifikat o'rnatish.

**Ishga tushirish:**
```bash
sudo ./setup-ssl.sh
```

Qo'ymalar:
- Domain nomi (masalan: agriculture.uz)
- Email address (sertifikat recovery uchun)

Script avtomatik:
- HTTPS sertifikat o'rnatadi
- Nginx konfiguratsiyasini yangilaydi
- Auto-renewal (har 3 oy) sozlaydi

---

### `update-deploy.sh` - Quick Update Script
Production-da yangi code deploy qilish (git pull, migrations, restart).

**Ishga tushirish:**
```bash
sudo ./update-deploy.sh
```

Avtomatik qiladi:
1. Git pull (latest code)
2. Python packages update
3. Django migrations
4. Static files collect
5. Services restart
6. Health check

---

## 🚀 Deployment Jarayoni

### 1-QADAM: Initial Setup

```bash
# Server ga kirish
ssh root@your-server-ip

# Repository clone
git clone https://github.com/Saidmirzo/agriculture.git
cd agriculture

# Scripts executable qilish
chmod +x *.sh

# Deploy script ishga tushirish
sudo ./deploy.sh
```

**Natija:** 15-20 minut ichida barcha services installda va ishga tushadi.

### 2-QADAM: Domain va SSL Setup

```bash
# SSL sertifikat o'rnatish
sudo ./setup-ssl.sh
```

Qo'ymalar:
- Your domain (masalan: agriculture.uz)
- Your email (masalan: admin@agriculture.uz)

**Natija:** HTTPS avtomatik faolashtiriladi, auto-renewal sozlanadi.

### 3-QADAM: Environment Variables Tekshirish

```bash
# .env fayl tekshirish va tahrirish
sudo nano /var/www/agriculture/.env
```

Muhim parametrlar:
```
DATABASE_URL=postgresql://agriculture:PASSWORD@localhost:5432/agriculture_db
DJANGO_SECRET_KEY=your-secret-key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
REDIS_URL=redis://localhost:6379/0
DEBUG=False
```

### 4-QADAM: Admin Account Yaratish

```bash
# Virtual environment activate
source /var/www/agriculture/venv/bin/activate

# Admin user yaratish
cd /var/www/agriculture
python manage.py createsuperuser
```

Qo'ymalar:
- Username: admin
- Email: admin@agriculture.uz
- Password: strong-password

### 5-QADAM: Tekshirish

```bash
# Services status
sudo systemctl status gunicorn_agriculture
sudo systemctl status daphne_agriculture
sudo systemctl status nginx

# Logs ko'rish
sudo journalctl -u gunicorn_agriculture -f
```

Browser orqali tekshirish:
- https://your-domain.com - Main page
- https://your-domain.com/admin - Admin panel
- https://your-domain.com/api - API

---

## 🔧 Asosiy Komandalari

### Services Boshqarish

```bash
# Status ko'rish
sudo systemctl status gunicorn_agriculture
sudo systemctl status daphne_agriculture
sudo systemctl status nginx

# Restart qilish
sudo systemctl restart gunicorn_agriculture
sudo systemctl restart daphne_agriculture

# Stop qilish
sudo systemctl stop gunicorn_agriculture
sudo systemctl start gunicorn_agriculture

# Logs ko'rish (real-time)
sudo journalctl -u gunicorn_agriculture -f
sudo journalctl -u daphne_agriculture -f
sudo journalctl -u nginx -f
```

### Database

```bash
# PostgreSQL connect
sudo -u postgres psql -d agriculture_db

# Backup qilish
sudo -u postgres pg_dump agriculture_db > backup.sql

# Restore qilish
sudo -u postgres psql agriculture_db < backup.sql

# Django shell
source /var/www/agriculture/venv/bin/activate
cd /var/www/agriculture
python manage.py shell
```

### Redis

```bash
# Redis test
redis-cli ping

# Monitor
redis-cli monitor

# Memory status
redis-cli INFO memory
```

### Nginx

```bash
# Config test
sudo nginx -t

# Restart
sudo systemctl restart nginx

# Logs
sudo tail -f /var/log/nginx/error.log
```

---

## 📊 Monitoring va Logs

### Gunicorn Logs
```bash
sudo journalctl -u gunicorn_agriculture -n 100
```

### Daphne Logs
```bash
sudo journalctl -u daphne_agriculture -n 100
```

### Nginx Logs
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### System Logs
```bash
sudo journalctl -xe
```

---

## 🔒 Security Best Practices

### 1. SSH Key Setup
```bash
# Public key qo'shish
echo "ssh-rsa AAAA..." >> ~/.ssh/authorized_keys

# Password login disable qilish
sudo nano /etc/ssh/sshd_config
# PasswordAuthentication no
sudo systemctl restart ssh
```

### 2. Firewall
```bash
# Status
sudo ufw status

# Rules qo'shish (agar kerak bo'lsa)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### 3. Regular Backups
```bash
# Database backup
sudo -u postgres pg_dump agriculture_db > /backups/agriculture_$(date +%Y%m%d).sql

# Code backup
tar -czf /backups/agriculture_code_$(date +%Y%m%d).tar.gz /var/www/agriculture
```

### 4. SSL Renewal Check
```bash
# Sertifikat status
sudo certbot certificates

# Renewal test
sudo certbot renew --dry-run
```

---

## 🆘 Troubleshooting

### Service failed to start

```bash
# Logs ko'rish
sudo journalctl -u gunicorn_agriculture -f

# Restart qilish
sudo systemctl restart gunicorn_agriculture

# Manual test
cd /var/www/agriculture
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### Database connection error

```bash
# PostgreSQL status
sudo systemctl status postgresql

# Credentials tekshirish
sudo -u postgres psql -l

# Connection test
psql -U agriculture -d agriculture_db -h localhost
```

### Redis connection error

```bash
# Redis status
sudo systemctl status redis-server

# Redis test
redis-cli ping

# Connection test
redis-cli -h localhost -p 6379
```

### Nginx 502 Bad Gateway

```bash
# Gunicorn/Daphne running?
ps aux | grep gunicorn
ps aux | grep daphne

# Logs
sudo journalctl -u gunicorn_agriculture -f
sudo journalctl -u daphne_agriculture -f

# Restart all
sudo systemctl restart gunicorn_agriculture daphne_agriculture nginx
```

---

## 📈 Production Checklist

- [ ] Domain nomi sozlangan
- [ ] SSL sertifikat o'rnatilgan (https)
- [ ] Database backup policy sozlangan
- [ ] Admin account yaratilgan
- [ ] Email/SMTP sozlangan
- [ ] Monitoring va alerting sozlangan
- [ ] Log rotation sozlangan
- [ ] Firewall sozlangan
- [ ] SSH key authentication sozlangan
- [ ] Regular updates scheduled

---

## 📞 Support va Masalalarni Xal Qilish

Masalalar bo'lsa:

1. Logs ko'rish: `sudo journalctl -u gunicorn_agriculture -f`
2. Status tekshirish: `sudo systemctl status gunicorn_agriculture`
3. Service restart: `sudo systemctl restart gunicorn_agriculture`
4. Manual test: `python manage.py runserver 0.0.0.0:8000`

---

## 🔄 Update va Maintenance

Har haftada:
```bash
sudo apt-get update && sudo apt-get upgrade -y
```

Yangi code deploy qilish:
```bash
sudo ./update-deploy.sh
```

Manual full update:
```bash
cd /var/www/agriculture
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn_agriculture daphne_agriculture
```

---

**Yasama: agriculture Backend Deployment**
**Oxirgi yangilash: 2024**
