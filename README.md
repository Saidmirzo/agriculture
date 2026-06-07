# 🌾 Agriculture Backend - Full Deployment Solution

![Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![Django](https://img.shields.io/badge/Django-5.1.4-darkgreen)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-blue)

Complete Django + Channels + Redis backend deployment solution for Ubuntu servers.

## 📋 Contents

```
📄 QUICK_START.md              - 30 sekundlik start guide
📄 DEPLOYMENT_GUIDE_UZ.md      - O'zbek tilida to'liq guide
📄 DEPLOYMENT_GUIDE_EN.md      - English version
📄 SCRIPTS_REFERENCE.md        - Scripts tafsiloti
📄 README.md                   - Bu fayl

🚀 DEPLOYMENT SCRIPTS:
📜 deploy.sh                   - Initial setup (birinchi ishga)
📜 setup-ssl.sh                - SSL/HTTPS setup
📜 update-deploy.sh            - Production update
📜 manage-services.sh          - Service management menu
📜 backup.sh                   - Backup/restore
```

---

## 🚀 Quick Start (3 Steps)

### 1. SSH into server
```bash
ssh root@your-server-ip
cd ~
```

### 2. Clone and prepare
```bash
git clone https://github.com/Saidmirzo/agriculture.git
cd agriculture
chmod +x *.sh
```

### 3. Deploy
```bash
sudo ./deploy.sh          # 20 minut
sudo ./setup-ssl.sh       # 5 minut
```

**Done!** 🎉 Your backend is now running on https://your-domain.com

---

## 📦 What Gets Installed

| Component | Version | Port | Purpose |
|-----------|---------|------|---------|
| **Ubuntu** | 20.04/22.04 | - | Server OS |
| **Nginx** | Latest | 80, 443 | Reverse Proxy |
| **Django** | 5.1.4 | - | Framework |
| **Gunicorn** | Latest | 8000 | HTTP API Server |
| **Daphne** | Latest | 8001 | WebSocket/ASGI |
| **PostgreSQL** | 14+ | 5432 | Database |
| **Redis** | Latest | 6379 | Cache |
| **Python** | 3.10+ | - | Runtime |

---

## 🎯 Features

✅ **One-Click Deployment** - Everything automated
✅ **Nginx Reverse Proxy** - Production-grade setup
✅ **PostgreSQL Database** - Secure and optimized
✅ **Redis Caching** - Performance boost
✅ **WebSocket Support** - Django Channels ready
✅ **HTTPS/SSL** - Free Let's Encrypt certificates
✅ **Auto-Renewal** - Certificate renewal scheduled
✅ **Systemd Services** - Auto-start and auto-restart
✅ **Firewall** - UFW configured
✅ **Backup Scripts** - Database and files backup
✅ **Monitoring** - Real-time logs and health checks

---

## 📖 Documentation

### For O'zbek speakers:
- [QUICK_START.md](QUICK_START.md) - 30 sekundlik start
- [DEPLOYMENT_GUIDE_UZ.md](DEPLOYMENT_GUIDE_UZ.md) - To'liq guide

### For English speakers:
- [DEPLOYMENT_GUIDE_EN.md](DEPLOYMENT_GUIDE_EN.md) - Complete guide

### Technical Reference:
- [SCRIPTS_REFERENCE.md](SCRIPTS_REFERENCE.md) - Scripts detailed info

---

## 🔧 Available Scripts

### 1. deploy.sh - Initial Setup
```bash
sudo ./deploy.sh
```
Birinchi marta ishga tushirish uchun. Barcha packages, database, services.

**Duration:** 15-20 minutes
**Output:** All services running

### 2. setup-ssl.sh - HTTPS Certificate
```bash
sudo ./setup-ssl.sh
```
Let's Encrypt orqali free HTTPS sertifikat.

**Duration:** 5-10 minutes
**Features:** Auto-renewal enabled

### 3. update-deploy.sh - Production Update
```bash
sudo ./update-deploy.sh
```
Yangi kod deploy qilish (git pull + migrations + restart).

**Duration:** 2-5 minutes
**Safety:** Health check included

### 4. manage-services.sh - Service Management
```bash
./manage-services.sh
```
Interactive menu - 13 ta option.

### 5. backup.sh - Backup and Restore
```bash
sudo ./backup.sh backup
sudo ./backup.sh restore-db file.sql.gz
sudo ./backup.sh list
```

---

## 🌐 Architecture

```
┌─────────────────────────────────────────────────┐
│                   INTERNET                      │
└──────────────────────┬──────────────────────────┘
                       │ HTTPS
        ┌──────────────┴──────────────┐
        │      Nginx Reverse Proxy     │
        │  (80→443, Load balance)      │
        └─┬──────────────────────┬────┘
          │                      │
          ↓                      ↓
      ┌────────┐            ┌─────────┐
      │HTTP/API│            │WebSocket│
      │Gunicorn│            │ Daphne  │
      │:8000   │            │ :8001   │
      └──┬─────┘            └────┬────┘
         │                       │
         └───────────┬───────────┘
                     ↓
        ┌────────────────────────┐
        │   PostgreSQL Database  │
        │   Port 5432            │
        └────────────────────────┘
        
        ┌────────────────────────┐
        │   Redis Cache          │
        │   Port 6379            │
        └────────────────────────┘
```

---

## 📊 Directory Structure

```
/var/www/agriculture/
├── manage.py              # Django management
├── requirements.txt       # Python packages
├── .env                   # Environment variables (SECURE)
├── core/                  # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── asgi.py
├── agriculture/           # Main application
├── static/                # Collected static files
├── public/                # Media files
├── venv/                  # Python virtual environment
└── DATABASE_CREDENTIALS.txt # Credentials (SECURE)
```

---

## 🔒 Security Features

✅ HTTPS/SSL with Let's Encrypt
✅ Automatic SSL renewal
✅ Firewall (UFW) enabled
✅ Security headers (HSTS, CSP, etc.)
✅ CSRF protection
✅ Secure session cookies
✅ Environment variables in .env
✅ PostgreSQL password protected
✅ Redis bound to localhost only
✅ Systemd service isolation

---

## 🆘 Troubleshooting

### Service issues
```bash
sudo journalctl -u gunicorn_agriculture -f
sudo systemctl restart gunicorn_agriculture
```

### Database issues
```bash
sudo systemctl status postgresql
sudo -u postgres psql agriculture_db
```

### Check all services
```bash
sudo systemctl status gunicorn_agriculture
sudo systemctl status daphne_agriculture
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis-server
```

### View Nginx errors
```bash
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

---

## 📈 Maintenance

### Daily
- Monitor error logs
- Check disk space
- Verify services running

### Weekly
```bash
sudo apt-get update && sudo apt-get upgrade -y
```

### Monthly
```bash
sudo certbot certificates
sudo backup.sh backup
```

---

## 🚀 Deployment Workflow

```
LOCAL DEVELOPMENT
        ↓
git commit && git push
        ↓
SSH to server
        ↓
sudo ./update-deploy.sh
        ↓
LIVE IN PRODUCTION
```

---

## 📋 Pre-Deployment Checklist

- [ ] Ubuntu 20.04 or 22.04 server ready
- [ ] SSH access with sudo privileges
- [ ] Domain name pointing to server IP
- [ ] 2GB+ RAM available
- [ ] 20GB+ disk space available
- [ ] Internet connectivity confirmed

## 📋 Post-Deployment Checklist

- [ ] HTTPS working (🔒 in browser)
- [ ] Admin panel accessible
- [ ] Database connection OK
- [ ] Redis connection OK
- [ ] WebSocket working
- [ ] Backups scheduled
- [ ] Monitoring configured
- [ ] SSL renewal verified

---

## 🔄 Update Workflow

### Deploy new code
```bash
# Local
git push origin main

# Server
sudo ./update-deploy.sh
```

### Manual full update
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

## 📊 Performance

- **Gunicorn Workers:** 4 (optimized for 2GB RAM)
- **Nginx Worker Connections:** 1024
- **Redis Max Memory:** 512MB
- **PostgreSQL:** Automatic query optimization
- **Gzip Compression:** Enabled for static files
- **Static File Caching:** 30 days

---

## 🔧 Common Commands

### View logs
```bash
# Real-time HTTP API
sudo journalctl -u gunicorn_agriculture -f

# Real-time WebSocket
sudo journalctl -u daphne_agriculture -f

# Real-time Nginx
sudo journalctl -u nginx -f
```

### Manage services
```bash
sudo systemctl status/start/stop/restart gunicorn_agriculture
sudo systemctl status/start/stop/restart daphne_agriculture
sudo systemctl status/start/stop/restart nginx
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

### Static files
```bash
python manage.py collectstatic --noinput
```

---

## 🌐 Accessing Your Application

After deployment:

| URL | Purpose |
|-----|---------|
| https://your-domain.com | Main application |
| https://your-domain.com/admin | Admin panel |
| https://your-domain.com/api | API documentation |
| https://your-domain.com/ws/ | WebSocket endpoint |

---

## 📞 Support

### Documentation
- Read full guides in DEPLOYMENT_GUIDE_UZ.md or EN.md
- Check SCRIPTS_REFERENCE.md for script details
- Review QUICK_START.md for quick help

### Troubleshooting
1. Check logs: `sudo journalctl -u gunicorn_agriculture -f`
2. Check status: `sudo systemctl status gunicorn_agriculture`
3. Check .env: `cat /var/www/agriculture/.env`

### GitHub
Report issues: https://github.com/Saidmirzo/agriculture/issues

---

## 📝 Configuration Files

### Environment Variables (.env)
```
DATABASE_URL=postgresql://...
DJANGO_SECRET_KEY=...
DEBUG=False
ALLOWED_HOSTS=...
REDIS_URL=redis://localhost:6379/0
```

### Nginx Config
```
/etc/nginx/sites-available/agriculture
- Reverse proxy to Gunicorn (8000)
- WebSocket proxy to Daphne (8001)
- Static file serving
- SSL/HTTPS configuration
```

### Systemd Services
```
/etc/systemd/system/gunicorn_agriculture.service
/etc/systemd/system/daphne_agriculture.service
```

---

## 🎓 Learning Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Gunicorn](https://gunicorn.org/)
- [Nginx](https://nginx.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [Redis](https://redis.io/)
- [Let's Encrypt](https://letsencrypt.org/)

---

## 📜 License

MIT License - feel free to use and modify

---

## 🤝 Contributing

Found a bug or have a suggestion? Open an issue on GitHub!

---

## 👨‍💻 Author

**Agriculture Backend Team**

---

## 📈 Version History

- **v1.0** (2024) - Initial release
  - Full deployment automation
  - SSL/HTTPS support
  - Backup and restore
  - Service management

---

## 🎉 Ready to Deploy?

```bash
# 1. Clone
git clone https://github.com/Saidmirzo/agriculture.git
cd agriculture

# 2. Make executable
chmod +x *.sh

# 3. Deploy
sudo ./deploy.sh

# 4. Setup SSL
sudo ./setup-ssl.sh

# 5. Done!
```

---

**Questions?** Read the guides or check GitHub issues.

**Happy Deploying!** 🚀

---

**Generated:** 2024
**Tested on:** Ubuntu 20.04, 22.04
**Components:** Django 5.1, PostgreSQL 14+, Redis 7.0+, Nginx Latest
