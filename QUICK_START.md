# 🚀 Agriculture Backend - Quick Start Deployment

Bu fayl sizning Django application-ni Ubuntu serverga deploy qilish uchun to'liq setup berilgan.

## ⚡ 30 Sekundlik Quick Start

```bash
# 1. Serverga SSH orqali kirish
ssh root@your-server-ip

# 2. Repository clone qilish
git clone https://github.com/Saidmirzo/agriculture.git
cd agriculture

# 3. Scripts executable qilish
chmod +x *.sh

# 4. Deploy qilish (15-20 minut davom etadi)
sudo ./deploy.sh

# 5. SSL setup (domain + email bilan)
sudo ./setup-ssl.sh
```

Hammasi shunday oddiy! ✅

---

## 📦 Nima O'rnatiladi?

| Komponent | Tafsilot | Port |
|-----------|---------|------|
| **Nginx** | Reverse Proxy | 80, 443 |
| **Gunicorn** | HTTP API Server | 8000 |
| **Daphne** | WebSocket/ASGI | 8001 |
| **PostgreSQL** | Database | 5432 |
| **Redis** | Cache | 6379 |
| **Django** | Framework | - |

---

## 📁 Deployment Scripts

### 1️⃣ `deploy.sh` - BIRINCHI MARTA ISHGA TUSHIRISH
```bash
sudo ./deploy.sh
```
**Murakkab setup:** Barcha packages, database, services, SSL (self-signed)

### 2️⃣ `setup-ssl.sh` - HTTPS SOZLASH
```bash
sudo ./setup-ssl.sh
```
**Let's Encrypt sertifikat:** Free HTTPS, auto-renewal

### 3️⃣ `update-deploy.sh` - PRODUCTION UPDATE
```bash
sudo ./update-deploy.sh
```
**Git pull + Migrations + Restart:** Yangi code deploy qilish

### 4️⃣ `manage-services.sh` - SERVICE MENU
```bash
./manage-services.sh
```
**13 ta option:** Status, logs, backup, restart, etc.

### 5️⃣ `backup.sh` - BACKUP/RESTORE
```bash
sudo ./backup.sh backup              # Full backup
sudo ./backup.sh restore-db file.sql.gz  # Restore
sudo ./backup.sh list               # List backups
```

---

## 🎯 Deployment Stages

### STAGE 1: Initial Setup (20 minut)
```bash
sudo ./deploy.sh
```
✅ System packages
✅ PostgreSQL setup
✅ Redis setup
✅ Python environment
✅ Gunicorn + Daphne
✅ Nginx sozlash
✅ All services running

**Natija:** `/var/www/agriculture/DATABASE_CREDENTIALS.txt` - credentials saqlanadi

### STAGE 2: SSL Certificate (5 minut)
```bash
sudo ./setup-ssl.sh
```
✅ Free HTTPS certificate
✅ Auto-renewal setup
✅ HTTP → HTTPS redirect

**Natija:** Domain orqali HTTPS ishlaydi

### STAGE 3: Verification (5 minut)
```bash
# Check services
sudo systemctl status gunicorn_agriculture
sudo systemctl status daphne_agriculture

# Check in browser
# https://your-domain.com
# https://your-domain.com/admin
```

---

## 🔧 Tez Komandalar

### Services Boshqarish
```bash
# Status ko'rish
sudo systemctl status gunicorn_agriculture

# Restart qilish
sudo systemctl restart gunicorn_agriculture

# Logs ko'rish (real-time)
sudo journalctl -u gunicorn_agriculture -f
```

### Database
```bash
# Connect
sudo -u postgres psql agriculture_db

# Backup
sudo -u postgres pg_dump agriculture_db > backup.sql

# Admin user
python manage.py createsuperuser
```

### Quick Deploy
```bash
cd /var/www/agriculture
sudo ./update-deploy.sh
```

---

## ⚙️ Configuration

### Environment Variables
```bash
# Edit .env
sudo nano /var/www/agriculture/.env
```

**Muhim o'zgaruvchanlar:**
```env
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DJANGO_SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://agriculture:PASSWORD@localhost:5432/agriculture_db
REDIS_URL=redis://localhost:6379/0
```

### Nginx Config
- Location: `/etc/nginx/sites-available/agriculture`
- Auto-restart: `sudo nginx -t && sudo systemctl restart nginx`

### SSL Renewal
```bash
# Test renewal
sudo certbot renew --dry-run

# Manual renewal
sudo certbot renew
```

---

## 🆘 Troubleshooting

### Service failed?
```bash
sudo journalctl -u gunicorn_agriculture -f
sudo systemctl restart gunicorn_agriculture
```

### Database error?
```bash
sudo systemctl status postgresql
sudo -u postgres psql agriculture_db
```

### 502 error?
```bash
ps aux | grep gunicorn
ps aux | grep daphne
sudo systemctl restart gunicorn_agriculture daphne_agriculture
```

---

## 📊 Directory Structure

```
/var/www/agriculture/
├── manage.py
├── requirements.txt
├── core/                    # Django settings
├── agriculture/             # App code
├── static/                  # Collected static files
├── public/                  # Media files
├── venv/                    # Virtual environment
├── .env                     # Environment variables
└── DATABASE_CREDENTIALS.txt # Credentials (secure)
```

---

## 🔒 Security

✅ HTTPS/SSL enabled
✅ Firewall configured
✅ Security headers
✅ CSRF protection
✅ PostgreSQL password protected
✅ Redis localhost only
✅ .env file secured

**Qo'shimcha (Manual):**
- SSH key authentication
- Regular backups
- Monitoring/alerts
- Fail2ban rate limiting

---

## 📈 Monitoring

### Real-time Logs
```bash
# HTTP API
sudo journalctl -u gunicorn_agriculture -f

# WebSocket
sudo journalctl -u daphne_agriculture -f

# Web server
sudo journalctl -u nginx -f
```

### Health Check
```bash
# Services running?
ps aux | grep gunicorn
ps aux | grep daphne
ps aux | grep nginx

# Ports listening?
sudo netstat -tlnp | grep LISTEN
```

---

## 🔄 Production Workflow

### Deploy new code
```bash
# Local
git add .
git commit -m "New feature"
git push origin main

# On server
cd /var/www/agriculture
sudo ./update-deploy.sh
```

### Database migration
```bash
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn_agriculture
```

---

## 📋 Pre-Deployment Checklist

- [ ] Domain nomi server IP-ga ishora qilmoqda
- [ ] SSH access tayyor
- [ ] Sudo privileges bor
- [ ] 2GB+ RAM mavjud
- [ ] 20GB+ disk space mavjud

## Post-Deployment Checklist

- [ ] HTTPS ishlaydi (🔒 simvoli bor)
- [ ] Admin panel kirish qilinadi
- [ ] Database connection OK
- [ ] Redis connection OK
- [ ] Static files yuklandi
- [ ] WebSocket ishlaydi
- [ ] Emails configured (agar kerak)
- [ ] Backups scheduled

---

## 📞 Help

**Logs ko'rish:**
```bash
sudo journalctl -u gunicorn_agriculture -f
```

**Services restart qilish:**
```bash
sudo systemctl restart gunicorn_agriculture daphne_agriculture nginx
```

**Database credentials:**
```bash
cat /var/www/agriculture/DATABASE_CREDENTIALS.txt
```

---

## 📚 Full Documentation

- 🇺🇿 **O'zbek tilida:** `DEPLOYMENT_GUIDE_UZ.md`
- 🇬🇧 **English version:** `DEPLOYMENT_GUIDE_EN.md`

---

## 🎓 Scripts Description

| Script | Tarmog'i | Ishga Tushirish | Vaqt |
|--------|----------|----------------|----- |
| `deploy.sh` | Initial setup | `sudo ./deploy.sh` | 15-20m |
| `setup-ssl.sh` | SSL certificate | `sudo ./setup-ssl.sh` | 5-10m |
| `update-deploy.sh` | Code update | `sudo ./update-deploy.sh` | 2-5m |
| `manage-services.sh` | Service menu | `./manage-services.sh` | - |
| `backup.sh` | Backup/restore | `sudo ./backup.sh` | varies |

---

## 🚀 Performance Tips

1. **Nginx caching** - Static files 30 days cached
2. **Database indexing** - Check slow queries
3. **Redis optimization** - Set maxmemory policy
4. **Gunicorn workers** - 4 workers default
5. **CDN integration** - Optional for media

---

## 📞 Support

Muammolar bo'lsa:

1. Check logs: `sudo journalctl -u gunicorn_agriculture -f`
2. Check services: `sudo systemctl status gunicorn_agriculture`
3. Read guide: `DEPLOYMENT_GUIDE_UZ.md`
4. GitHub issues: https://github.com/Saidmirzo/agriculture/issues

---

**🎉 Tayyor? Boshlaylik!**

```bash
sudo ./deploy.sh
```

---

**Version:** 1.0
**Last Updated:** 2024
**Author:** Agriculture Backend Team
