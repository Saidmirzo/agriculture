#!/bin/bash

#############################################################################
# Agriculture Backend - Full Update & Deploy Script
# Repository update + Migrations + Services restart
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

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

#############################################################################
# MAIN DEPLOYMENT
#############################################################################

log_info "Starting Agriculture Backend Update & Deploy..."
echo ""

# 1. Git update
log_info "[1/6] Git repository update..."
cd "$APP_DIR"
sudo -u $APP_USER git fetch origin
sudo -u $APP_USER git pull origin main
log_info "✓ Repository updated"
echo ""

# 2. Install new requirements
log_info "[2/6] Installing/updating Python packages..."
source "$VENV_DIR/bin/activate"
"$VENV_DIR/bin/pip" install --upgrade pip setuptools wheel
"$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"
log_info "✓ Packages installed"
echo ""

# 3. Database migrations
log_info "[3/6] Running Django migrations..."
cd "$APP_DIR"
"$VENV_DIR/bin/python" manage.py migrate --noinput
log_info "✓ Migrations completed"
echo ""

# 4. Collect static files
log_info "[4/6] Collecting static files..."
"$VENV_DIR/bin/python" manage.py collectstatic --noinput
log_info "✓ Static files collected"
echo ""

# 5. Restart services
log_info "[5/6] Restarting services..."
sudo systemctl restart gunicorn_agriculture
sudo systemctl restart daphne_agriculture
log_info "✓ Services restarted"
echo ""

# 6. Health check
log_info "[6/6] Health check..."
sleep 2

GUNICORN_STATUS=$(sudo systemctl is-active gunicorn_agriculture)
DAPHNE_STATUS=$(sudo systemctl is-active daphne_agriculture)
NGINX_STATUS=$(sudo systemctl is-active nginx)

if [ "$GUNICORN_STATUS" = "active" ] && [ "$DAPHNE_STATUS" = "active" ] && [ "$NGINX_STATUS" = "active" ]; then
    log_info "✓ All services are running!"
    echo ""
    log_info "✓ DEPLOYMENT SUCCESSFUL!"
else
    log_error "Some services are not running!"
    echo "Gunicorn: $GUNICORN_STATUS"
    echo "Daphne: $DAPHNE_STATUS"
    echo "Nginx: $NGINX_STATUS"
    exit 1
fi

echo ""
log_info "Recent logs:"
echo "============"
sudo journalctl -u gunicorn_agriculture -n 5 --no-pager | sed 's/^/  /'
echo ""
log_info "Deploy completed at $(date '+%Y-%m-%d %H:%M:%S')"
