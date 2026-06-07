#!/bin/bash

#############################################################################
# Agriculture Backend - Restart/Update Script
# Services qayta ishga tushirish va update qilish
#############################################################################

set -e

APP_DIR="/var/www/agriculture"
VENV_DIR="${APP_DIR}/venv"
APP_USER="www-data"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Menyu
echo "Agriculture Backend Services Menu"
echo "===================================="
echo "1. Services status ko'rish"
echo "2. Services qayta ishga tushirish"
echo "3. Git pull (update) qilish"
echo "4. Django migrations qilish"
echo "5. Static files collect qilish"
echo "6. Logs ko'rish (Gunicorn)"
echo "7. Logs ko'rish (Daphne)"
echo "8. Logs ko'rish (Nginx)"
echo "9. Redis test qilish"
echo "10. Database backup qilish"
echo "11. Services stop qilish"
echo "12. Services start qilish"
echo "13. SSH key qo'shish"
echo ""
read -p "Tanlang (1-13): " choice

case $choice in
    1)
        log_info "Services status..."
        sudo systemctl status gunicorn_agriculture --no-pager
        sudo systemctl status daphne_agriculture --no-pager
        sudo systemctl status nginx --no-pager
        sudo systemctl status postgresql --no-pager
        sudo systemctl status redis-server --no-pager
        ;;
    2)
        log_info "Services qayta ishga tushirish..."
        sudo systemctl restart gunicorn_agriculture
        sudo systemctl restart daphne_agriculture
        sudo systemctl restart nginx
        log_info "✓ Services restarted"
        ;;
    3)
        log_info "Git pull qilyapman..."
        cd "$APP_DIR"
        sudo -u $APP_USER git pull origin main
        log_info "✓ Update complete"
        ;;
    4)
        log_info "Django migrations..."
        cd "$APP_DIR"
        source "$VENV_DIR/bin/activate"
        python manage.py migrate --noinput
        log_info "✓ Migrations complete"
        ;;
    5)
        log_info "Static files collecting..."
        cd "$APP_DIR"
        source "$VENV_DIR/bin/activate"
        python manage.py collectstatic --noinput
        log_info "✓ Static files collected"
        ;;
    6)
        log_info "Gunicorn logs (last 50 lines)..."
        sudo journalctl -u gunicorn_agriculture -n 50 --no-pager
        ;;
    7)
        log_info "Daphne logs (last 50 lines)..."
        sudo journalctl -u daphne_agriculture -n 50 --no-pager
        ;;
    8)
        log_info "Nginx logs (last 50 lines)..."
        sudo journalctl -u nginx -n 50 --no-pager
        ;;
    9)
        log_info "Redis test..."
        redis-cli ping
        redis-cli INFO server | head -10
        ;;
    10)
        log_info "PostgreSQL backup qilyapman..."
        BACKUP_DIR="/var/backups/agriculture"
        sudo mkdir -p "$BACKUP_DIR"
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        sudo -u postgres pg_dump agriculture_db > "$BACKUP_DIR/agriculture_db_$TIMESTAMP.sql"
        log_info "✓ Backup saved: $BACKUP_DIR/agriculture_db_$TIMESTAMP.sql"
        ;;
    11)
        log_warn "Services stop qilyapman..."
        sudo systemctl stop gunicorn_agriculture
        sudo systemctl stop daphne_agriculture
        log_info "✓ Services stopped"
        ;;
    12)
        log_info "Services start qilyapman..."
        sudo systemctl start gunicorn_agriculture
        sudo systemctl start daphne_agriculture
        log_info "✓ Services started"
        ;;
    13)
        log_info "SSH public key qo'shing:"
        read -p "SSH public key: " ssh_key
        echo "$ssh_key" >> ~/.ssh/authorized_keys
        log_info "✓ SSH key added"
        ;;
    *)
        log_warn "Noto'g'ri tanlov"
        ;;
esac
