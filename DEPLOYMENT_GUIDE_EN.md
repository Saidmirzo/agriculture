# Agriculture Backend Deployment Guide (English)

## 📋 Prerequisites and Preparation

### 1. Server Requirements
- Ubuntu 20.04 or 22.04
- Minimum 2GB RAM (4GB recommended)
- Minimum 20GB disk space
- SSH access with sudo privileges
- Domain name pointing to server IP

### 2. Prepare Repository
```bash
# SSH into server
ssh root@your-server-ip

# Clone repository
git clone https://github.com/Saidmirzo/agriculture.git
cd agriculture
```

### 3. Make Scripts Executable
```bash
chmod +x deploy.sh
chmod +x manage-services.sh
chmod +x setup-ssl.sh
chmod +x update-deploy.sh
```

---

## 🚀 Deployment Steps

### STEP 1: Initial Deployment (15-20 minutes)

```bash
# Run main deployment script
sudo ./deploy.sh
```

**What it does:**
- Installs system packages (nginx, postgresql, redis, python3, etc.)
- Creates PostgreSQL database and user
- Sets up Redis server
- Creates Python virtual environment
- Installs Django packages
- Configures environment variables (.env)
- Runs Django migrations
- Sets up Gunicorn (HTTP API server)
- Sets up Daphne (WebSocket/ASGI server)
- Configures Nginx reverse proxy
- Creates systemd services
- Configures firewall
- Starts all services

**Output:**
- Database credentials saved to: `/var/www/agriculture/DATABASE_CREDENTIALS.txt`
- All services running and enabled for auto-start

### STEP 2: Configure SSL/HTTPS

```bash
# Run SSL setup script
sudo ./setup-ssl.sh
```

**Inputs:**
- Domain name (e.g., agriculture.com)
- Email address (for Let's Encrypt recovery)

**What it does:**
- Obtains free SSL certificate from Let's Encrypt
- Configures Nginx for HTTPS
- Sets up automatic certificate renewal (every 90 days)
- Redirects HTTP to HTTPS

### STEP 3: Verify Environment Configuration

```bash
# Edit environment variables
sudo nano /var/www/agriculture/.env
```

**Important settings to verify/update:**
```
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DJANGO_SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://agriculture:PASSWORD@localhost:5432/agriculture_db
REDIS_URL=redis://localhost:6379/0
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

### STEP 4: Create Admin User

```bash
# Activate virtual environment
source /var/www/agriculture/venv/bin/activate

# Create admin account
cd /var/www/agriculture
python manage.py createsuperuser
```

### STEP 5: Verify Deployment

```bash
# Check service status
sudo systemctl status gunicorn_agriculture
sudo systemctl status daphne_agriculture
sudo systemctl status nginx

# View real-time logs
sudo journalctl -u gunicorn_agriculture -f
```

**Test in browser:**
- https://your-domain.com - Main application
- https://your-domain.com/admin - Admin panel
- https://your-domain.com/api - API documentation

---

## 📊 Script Information

### `deploy.sh` - Main Deployment Script

Complete initial setup. Run once per server.

**Components installed:**
- ✅ System packages (nginx, postgresql, redis, python3)
- ✅ PostgreSQL database and user
- ✅ Redis server
- ✅ Python 3 virtual environment
- ✅ Django packages from requirements.txt
- ✅ Gunicorn (HTTP API server, port 8000)
- ✅ Daphne (WebSocket/ASGI server, port 8001)
- ✅ Nginx reverse proxy (ports 80, 443)
- ✅ Systemd services for auto-start and auto-restart
- ✅ Firewall configuration
- ✅ Self-signed SSL certificate (replaced by Let's Encrypt later)

### `manage-services.sh` - Service Management Menu

Interactive menu for common tasks.

**Options:**
1. View service status
2. Restart services
3. Git pull (update code)
4. Run Django migrations
5. Collect static files
6. View Gunicorn logs
7. View Daphne logs
8. View Nginx logs
9. Test Redis connection
10. Database backup
11. Stop services
12. Start services
13. Add SSH key

```bash
./manage-services.sh
```

### `setup-ssl.sh` - SSL Certificate Setup

Install and configure HTTPS with Let's Encrypt.

```bash
sudo ./setup-ssl.sh
```

**Automatically:**
- Installs certbot if needed
- Obtains SSL certificate
- Configures Nginx for HTTPS
- Sets up auto-renewal via cron

### `update-deploy.sh` - Quick Production Update

Deploy new code changes safely.

```bash
sudo ./update-deploy.sh
```

**Performs:**
1. Git pull latest code
2. Install/update Python packages
3. Run Django migrations
4. Collect static files
5. Restart services
6. Health check

---

## 🔧 Common Commands

### Service Management

```bash
# View status
sudo systemctl status gunicorn_agriculture
sudo systemctl status daphne_agriculture
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis-server

# Restart services
sudo systemctl restart gunicorn_agriculture
sudo systemctl restart daphne_agriculture

# View logs (real-time)
sudo journalctl -u gunicorn_agriculture -f
sudo journalctl -u daphne_agriculture -f
sudo journalctl -u nginx -f
```

### Database Management

```bash
# Connect to PostgreSQL
sudo -u postgres psql -d agriculture_db

# Create database backup
sudo -u postgres pg_dump agriculture_db > backup_$(date +%Y%m%d).sql

# Restore from backup
sudo -u postgres psql agriculture_db < backup_$(date +%Y%m%d).sql

# Django management
source /var/www/agriculture/venv/bin/activate
cd /var/www/agriculture
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### Redis Commands

```bash
# Test connection
redis-cli ping

# View memory usage
redis-cli INFO memory

# Clear cache
redis-cli FLUSHALL

# Monitor commands
redis-cli monitor
```

### Nginx

```bash
# Test configuration
sudo nginx -t

# Restart
sudo systemctl restart nginx

# View logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────┐
│           INTERNET / Users              │
└──────────────────┬──────────────────────┘
                   │
                   ↓ (HTTPS)
        ┌──────────────────────┐
        │   Nginx Reverse      │
        │   Proxy (ports       │
        │   80, 443)           │
        └──────┬────────────────┘
               │
        ┌──────┴─────────┐
        ↓                ↓
    ┌────────┐      ┌─────────┐
    │ HTTP   │      │WebSocket│
    │API     │      │/ASGI    │
    │-----   │      │-----    │
    │Gunicorn│      │ Daphne  │
    │Port    │      │ Port    │
    │8000    │      │ 8001    │
    └───┬────┘      └────┬────┘
        │                │
        └────────┬───────┘
                 ↓
        ┌───────────────────┐
        │   PostgreSQL      │
        │   Database        │
        │   Port 5432       │
        └───────────────────┘
        
        ┌───────────────────┐
        │   Redis Cache     │
        │   Port 6379       │
        └───────────────────┘
        
        ┌───────────────────┐
        │   Django App      │
        │   /var/www/       │
        │   agriculture     │
        └───────────────────┘
```

---

## 🔒 Security Features

### Automated
- ✅ HTTPS/SSL with Let's Encrypt
- ✅ Automatic SSL renewal (every 90 days)
- ✅ Firewall enabled (UFW)
- ✅ Security headers (HSTS, X-Frame-Options, etc.)
- ✅ CSRF protection
- ✅ Session cookie secure flags
- ✅ Environment variables in .env (not in code)

### Manual Setup Recommended
- [ ] Configure SSH key authentication (disable password login)
- [ ] Set up regular backups
- [ ] Configure monitoring and alerting
- [ ] Set up fail2ban for rate limiting
- [ ] Configure Sentry for error tracking
- [ ] Enable logging and log rotation

---

## 🆘 Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u gunicorn_agriculture -n 50

# Check syntax
cd /var/www/agriculture
source venv/bin/activate
python manage.py check

# Try manual start
python manage.py runserver 0.0.0.0:8000
```

### Database Connection Error

```bash
# Check PostgreSQL
sudo systemctl status postgresql
sudo -u postgres psql -l

# Test connection
psql -U agriculture -d agriculture_db -h localhost

# Check credentials in .env
cat /var/www/agriculture/.env | grep DATABASE
```

### Redis Connection Error

```bash
# Check Redis
sudo systemctl status redis-server
redis-cli ping

# Check port
sudo netstat -tlnp | grep 6379
```

### 502 Bad Gateway Error

```bash
# Check if services are running
ps aux | grep gunicorn
ps aux | grep daphne

# Restart services
sudo systemctl restart gunicorn_agriculture daphne_agriculture

# Check Nginx error log
sudo tail -f /var/log/nginx/error.log
```

### High Memory Usage

```bash
# Check memory
free -h

# Check Redis memory
redis-cli INFO memory

# Clear old sessions
python manage.py clearsessions
```

---

## 📈 Monitoring and Maintenance

### Regular Checks

```bash
# Weekly system update
sudo apt-get update && sudo apt-get upgrade -y

# Monthly SSL certificate check
sudo certbot certificates

# Monthly database backup verification
ls -lh /backups/
```

### Performance Monitoring

```bash
# CPU and Memory
top -b -n 1

# Disk usage
df -h
du -sh /var/www/agriculture

# Network
netstat -tuln

# Active connections
netstat -ptu
```

### Log Analysis

```bash
# Recent errors
sudo journalctl -u gunicorn_agriculture -p err

# Slow requests
grep "took" /var/log/agriculture/access.log | tail -20

# Failed logins
grep "failed" /var/log/auth.log
```

---

## 🔄 Deployment Updates

### Push Updates to Production

```bash
# Local development
git add .
git commit -m "New feature"
git push origin main

# On server
cd /var/www/agriculture
sudo ./update-deploy.sh
```

### Manual Update Process

```bash
# Pull latest code
cd /var/www/agriculture
sudo git pull origin main

# Activate environment
source venv/bin/activate

# Install any new packages
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart gunicorn_agriculture daphne_agriculture
```

---

## 📋 Production Checklist

Before going live:

- [ ] Domain name configured and pointing to server
- [ ] SSL certificate installed and working (https://)
- [ ] Django DEBUG=False
- [ ] ALLOWED_HOSTS configured correctly
- [ ] SECRET_KEY changed from default
- [ ] Admin user created
- [ ] Database backup tested
- [ ] Email/SMTP configured (if needed)
- [ ] Error tracking (Sentry) configured
- [ ] Logging configured
- [ ] Firewall rules set
- [ ] SSH key authentication enabled
- [ ] Monitoring alerts configured
- [ ] Regular backup schedule set

---

## 📞 Support

For issues:

1. **Check logs:** `sudo journalctl -u gunicorn_agriculture -f`
2. **Check status:** `sudo systemctl status gunicorn_agriculture`
3. **Restart service:** `sudo systemctl restart gunicorn_agriculture`
4. **Check .env:** `cat /var/www/agriculture/.env`
5. **Database backup:** `sudo -u postgres pg_dump agriculture_db > backup.sql`

---

## 📚 Useful Links

- Django Documentation: https://docs.djangoproject.com/
- Gunicorn: https://gunicorn.org/
- Daphne: https://github.com/django/daphne
- Nginx: https://nginx.org/
- PostgreSQL: https://www.postgresql.org/
- Redis: https://redis.io/
- Let's Encrypt: https://letsencrypt.org/
- Ubuntu Server Guide: https://ubuntu.com/server/docs

---

**Agriculture Backend Deployment**
**Version: 1.0**
**Last Updated: 2024**
