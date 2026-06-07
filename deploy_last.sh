APP_NAME="agriculture"
APP_USER="www-data"
APP_DIR="/var/www/agriculture"
VENV_DIR="${APP_DIR}/venv"
REPO_URL="https://github.com/Saidmirzo/agriculture"
DOMAIN="your-domain.com"  # O'zgartirish kerak
EMAIL="saidmirzobahromov88@gmail.com"  # SSL sertifikat uchun
DB_NAME="agriculture_db"
DB_USER="agriculture"
DB_PASSWORD="db123456"  # Random password
REDIS_PORT=6379
GUNICORN_PORT=8000
DAPHNE_PORT=8001

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_info "Let's Encrypt SSL sertifikatini o'rnatish..."

if [ -z "$DOMAIN" ] || [ "$DOMAIN" = "your-domain.com" ]; then
    log_warn "Domain nomi o'zgartirilmagan, SSL skipped. Keyin qo'lda qilamiz."
    log_warn "SSL o'rnatish uchun: sudo certbot --nginx -d $DOMAIN"
else
    sudo certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" \
        --non-interactive --agree-tos -m "$EMAIL" 2>/dev/null || \
    log_warn "SSL sertifikat avtomatik o'rnatilmadi, qo'lda qiling"
fi

#############################################################################
# 12. SYSTEMD SERVICES
#############################################################################
log_info "Systemd services faollashtirish..."

sudo systemctl daemon-reload
sudo systemctl enable gunicorn_agriculture.service
sudo systemctl enable daphne_agriculture.service
sudo systemctl enable redis-server
sudo systemctl enable postgresql
sudo systemctl enable nginx

#############################################################################
# 13. LOGGING SETUP
#############################################################################
log_info "Logging va monitoring sozlash..."

# Create log directory
sudo mkdir -p /var/log/agriculture
sudo chown $APP_USER:$APP_USER /var/log/agriculture

# Log rotation
sudo tee /etc/logrotate.d/agriculture > /dev/null << EOF
/var/log/agriculture/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 $APP_USER $APP_USER
    sharedscripts
    postrotate
        systemctl reload gunicorn_agriculture > /dev/null 2>&1 || true
        systemctl reload daphne_agriculture > /dev/null 2>&1 || true
    endscript
}
EOF

log_info "✓ Logging sozlandi"

#############################################################################
# 14. FIREWALL SETUP
#############################################################################
log_info "Firewall sozlash..."

sudo ufw --force enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS

log_info "✓ Firewall sozlandi"

#############################################################################
# 15. SERVICES START
#############################################################################
log_info "Barcha services ishga tushirish..."

sudo systemctl restart postgresql
sudo systemctl restart redis-server
sudo systemctl restart gunicorn_agriculture
sudo systemctl restart daphne_agriculture
sudo systemctl restart nginx

# Wait for services to start
sleep 3

# Check service status
log_info "Service status tekshirilmoqda..."
sudo systemctl status gunicorn_agriculture --no-pager | grep Active
sudo systemctl status daphne_agriculture --no-pager | grep Active
sudo systemctl status redis-server --no-pager | grep Active
sudo systemctl status postgresql --no-pager | grep Active
sudo systemctl status nginx --no-pager | grep Active

#############################################################################
# 16. DATABASE CREDENTIALS FILE
#############################################################################
sudo tee /var/www/agriculture/DATABASE_CREDENTIALS.txt > /dev/null << EOF
=== Agriculture Backend Deployment Credentials ===

Database Credentials:
- Database Name: $DB_NAME
- Database User: $DB_USER
- Database Password: $DB_PASSWORD
- Database Host: localhost
- Database Port: 5432

Redis:
- Host: localhost
- Port: $REDIS_PORT

Nginx:
- Domain: $DOMAIN
- HTTP Port: 80
- HTTPS Port: 443

Gunicorn:
- Port: $GUNICORN_PORT
- Workers: 4

Daphne (ASGI):
- Port: $DAPHNE_PORT

Services:
- Gunicorn service: gunicorn_agriculture
- Daphne service: daphne_agriculture
- PostgreSQL service: postgresql
- Redis service: redis-server
- Nginx service: nginx

Useful Commands:
- Service status: sudo systemctl status gunicorn_agriculture
- View logs: sudo journalctl -u gunicorn_agriculture -n 100 -f
- Restart services: sudo systemctl restart gunicorn_agriculture daphne_agriculture
- Check Redis: redis-cli ping
- Django shell: source /var/www/agriculture/venv/bin/activate && cd /var/www/agriculture && python manage.py shell
EOF

sudo chown root:root /var/www/agriculture/DATABASE_CREDENTIALS.txt
sudo chmod 600 /var/www/agriculture/DATABASE_CREDENTIALS.txt

#############################################################################
# 17. SUMMARY
#############################################################################
log_info "=================================================="
log_info "✓ DEPLOYMENT COMPLETE!"
log_info "=================================================="
echo ""
log_info "Important URLs and Credentials:"
echo "   - Website: https://$DOMAIN"
echo "   - API: https://$DOMAIN/api/"
echo "   - Admin: https://$DOMAIN/admin/"
echo ""
log_info "Database Credentials:"
echo "   - Database: $DB_NAME"
echo "   - User: $DB_USER"
echo "   - Password: $DB_PASSWORD (raddiy.txt da saqlangan)"
echo ""
log_info "Services:"
echo "   - Gunicorn (HTTP API): port $GUNICORN_PORT"
echo "   - Daphne (WebSocket): port $DAPHNE_PORT"
echo "   - Redis: port $REDIS_PORT"
echo "   - PostgreSQL: port 5432"
echo "   - Nginx: ports 80, 443"
echo ""
log_info "Log viewini commands:"
echo "   - sudo journalctl -u gunicorn_agriculture -f"
echo "   - sudo journalctl -u daphne_agriculture -f"
echo "   - sudo journalctl -u nginx -f"
echo ""
log_info "Next Steps (KEYIN QO'LISH KERAK):"
echo "   1. Domain nomini va email-ni .env faylga qo'shing"
echo "   2. SSL sertifikatini Let's Encrypt bilan yangilang:"
echo "      sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"
echo "   3. Django SECRET_KEY ni o'zgartiring"
echo "   4. Database credentials faylni o'qing:"
echo "      cat /var/www/agriculture/DATABASE_CREDENTIALS.txt"
echo ""
log_info "=================================================="
