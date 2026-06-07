#!/usr/bin/env bash

#############################################################################
# Agriculture Backend Deployment Script
# AlmaLinux 8.10 + Django + Nginx + Gunicorn + Daphne + Redis + MariaDB
#############################################################################

set -Eeuo pipefail

# CONFIGURATION
APP_NAME="agriculture"
APP_USER="nginx"
APP_GROUP="nginx"
APP_DIR="/var/www/agriculture"
VENV_DIR="${APP_DIR}/venv"
REPO_URL="https://github.com/Saidmirzo/agriculture"
REPO_BRANCH="main"

DOMAIN="your-domain.com"                 # O'zgartiring
EMAIL="saidmirzobahromov88@gmail.com"    # SSL sertifikat uchun

# core/settings.py hozir MySQL/MariaDB uchun shu qiymatlarni ishlatyapti.
DB_NAME="agriculture_db"
DB_USER="agriculture_user"
DB_PASSWORD="agriculture_password"

REDIS_PORT=6379
GUNICORN_PORT=8000
DAPHNE_PORT=8001
PYTHON_BIN="python3.11"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

require_root() {
    if [ "$(id -u)" -ne 0 ]; then
        log_error "Bu script root huquqi bilan ishga tushishi kerak:"
        echo "sudo bash deploy.sh"
        exit 1
    fi
}

run_as_app_user() {
    runuser -u "$APP_USER" -- "$@"
}

write_credentials_file() {
    cat > "$APP_DIR/DATABASE_CREDENTIALS.txt" << EOF
=== Agriculture Backend Deployment Credentials ===

Database:
- Engine: MariaDB/MySQL
- Database Name: $DB_NAME
- Database User: $DB_USER
- Database Password: $DB_PASSWORD
- Database Host: localhost
- Database Port: 3306

Redis:
- Host: localhost
- Port: $REDIS_PORT

Nginx:
- Domain: $DOMAIN
- HTTP Port: 80
- HTTPS Port: 443

Services:
- Gunicorn: gunicorn_${APP_NAME}.service
- Daphne: daphne_${APP_NAME}.service
- MariaDB: mariadb.service
- Redis: redis.service
- Nginx: nginx.service

Useful Commands:
- sudo systemctl status gunicorn_${APP_NAME} daphne_${APP_NAME} nginx
- sudo journalctl -u gunicorn_${APP_NAME} -n 100 -f
- sudo journalctl -u daphne_${APP_NAME} -n 100 -f
- redis-cli ping
- source $VENV_DIR/bin/activate && cd $APP_DIR && python manage.py shell
EOF

    chown root:"$APP_GROUP" "$APP_DIR/DATABASE_CREDENTIALS.txt"
    chmod 0640 "$APP_DIR/DATABASE_CREDENTIALS.txt"
}

require_root

log_info "AlmaLinux versiyasi tekshirilmoqda..."
if [ -f /etc/almalinux-release ]; then
    cat /etc/almalinux-release
else
    log_warn "/etc/almalinux-release topilmadi. Script AlmaLinux 8.10 uchun yozilgan."
fi

#############################################################################
# 1. SYSTEM PACKAGES
#############################################################################
log_info "[1/13] System paketlar o'rnatilmoqda..."

dnf install -y dnf-plugins-core
dnf config-manager --set-enabled powertools >/dev/null 2>&1 || true
dnf config-manager --set-enabled crb >/dev/null 2>&1 || true
dnf install -y epel-release

dnf install -y \
    git \
    curl \
    wget \
    gcc \
    make \
    openssl \
    openssl-devel \
    pkgconf-pkg-config \
    "${PYTHON_BIN}" \
    "${PYTHON_BIN}-devel" \
    "${PYTHON_BIN}-pip" \
    mariadb-server \
    mariadb-devel \
    redis \
    nginx \
    certbot \
    python3-certbot-nginx \
    firewalld \
    policycoreutils-python-utils

log_info "System paketlar tayyor."

#############################################################################
# 2. SERVICES BASE SETUP
#############################################################################
log_info "[2/13] MariaDB, Redis, Nginx va firewalld yoqilmoqda..."

systemctl enable --now mariadb
systemctl enable --now redis
systemctl enable --now nginx
systemctl enable --now firewalld

#############################################################################
# 3. DATABASE SETUP
#############################################################################
log_info "[3/13] MariaDB database va user sozlanmoqda..."

mysql << EOF
CREATE DATABASE IF NOT EXISTS \`$DB_NAME\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';
ALTER USER '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EOF

log_info "MariaDB sozlandi: $DB_NAME / $DB_USER"

#############################################################################
# 4. APPLICATION DIRECTORY
#############################################################################
# log_info "[4/13] Ilova katalogi tayyorlanmoqda..."

# install -d -m 0755 -o "$APP_USER" -g "$APP_GROUP" "$APP_DIR"

# if [ ! -d "$APP_DIR/.git" ]; then
#     if [ -z "$(find "$APP_DIR" -mindepth 1 -maxdepth 1 2>/dev/null)" ]; then
#         run_as_app_user git clone --branch "$REPO_BRANCH" "$REPO_URL" "$APP_DIR"
#     else
#         log_warn "$APP_DIR bo'sh emas va git repository emas. Clone o'tkazib yuborildi."
#     fi
# else
#     log_info "Repository mavjud, yangilanmoqda..."
#     cd "$APP_DIR"
#     run_as_app_user git fetch origin
#     run_as_app_user git checkout "$REPO_BRANCH"
#     run_as_app_user git pull --ff-only origin "$REPO_BRANCH"
# fi

# chown -R "$APP_USER:$APP_GROUP" "$APP_DIR"

#############################################################################
# 5. PYTHON VIRTUAL ENVIRONMENT
#############################################################################
log_info "[5/13] Python virtual environment va dependencylar o'rnatilmoqda..."

if [ ! -d "$VENV_DIR" ]; then
    run_as_app_user "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

run_as_app_user "$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel
run_as_app_user "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"

#############################################################################
# 6. LOCAL ENV FILE
#############################################################################
log_info "[6/13] .env fayli yozilmoqda..."

if [ ! -f "$APP_DIR/.env" ]; then
    cat > "$APP_DIR/.env" << EOF
DEBUG=False
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN
DATABASE_NAME=$DB_NAME
DATABASE_USER=$DB_USER
DATABASE_PASSWORD=$DB_PASSWORD
DATABASE_HOST=localhost
DATABASE_PORT=3306
REDIS_URL=redis://127.0.0.1:$REDIS_PORT/0
DJANGO_SECRET_KEY=$(openssl rand -base64 48)
EOF
    chown "$APP_USER:$APP_GROUP" "$APP_DIR/.env"
    chmod 0600 "$APP_DIR/.env"
else
    log_warn ".env allaqachon mavjud, ustidan yozilmadi."
fi

#############################################################################
# 7. DJANGO SETUP
#############################################################################
log_info "[7/13] Django migrations va static fayllar..."

cd "$APP_DIR"
run_as_app_user "$VENV_DIR/bin/python" manage.py migrate --noinput
run_as_app_user "$VENV_DIR/bin/python" manage.py collectstatic --noinput

#############################################################################
# 8. GUNICORN SYSTEMD SERVICE
#############################################################################
log_info "[8/13] Gunicorn systemd service yozilmoqda..."

cat > "/etc/systemd/system/gunicorn_${APP_NAME}.service" << EOF
[Unit]
Description=Gunicorn service for $APP_NAME
After=network.target mariadb.service redis.service
Requires=mariadb.service redis.service

[Service]
Type=simple
User=$APP_USER
Group=$APP_GROUP
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=$VENV_DIR/bin/gunicorn \\
    --workers 4 \\
    --worker-class sync \\
    --bind 127.0.0.1:$GUNICORN_PORT \\
    --timeout 120 \\
    --access-logfile - \\
    --error-logfile - \\
    core.wsgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

#############################################################################
# 9. DAPHNE SYSTEMD SERVICE
#############################################################################
log_info "[9/13] Daphne systemd service yozilmoqda..."

cat > "/etc/systemd/system/daphne_${APP_NAME}.service" << EOF
[Unit]
Description=Daphne ASGI service for $APP_NAME
After=network.target mariadb.service redis.service
Requires=mariadb.service redis.service

[Service]
Type=simple
User=$APP_USER
Group=$APP_GROUP
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=$VENV_DIR/bin/daphne -b 127.0.0.1 -p $DAPHNE_PORT core.asgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

#############################################################################
# 10. NGINX CONFIGURATION
#############################################################################
log_info "[10/13] Nginx konfiguratsiyasi yozilmoqda..."

cat > "/etc/nginx/conf.d/${APP_NAME}.conf" << EOF
upstream ${APP_NAME}_gunicorn {
    server 127.0.0.1:$GUNICORN_PORT;
}

upstream ${APP_NAME}_daphne {
    server 127.0.0.1:$DAPHNE_PORT;
}

server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN www.$DOMAIN;

    client_max_body_size 20M;

    location /static/ {
        alias $APP_DIR/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias $APP_DIR/public/;
        expires 7d;
    }

    location /ws/ {
        proxy_pass http://${APP_NAME}_daphne;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }

    location / {
        proxy_pass http://${APP_NAME}_gunicorn;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
    }
}
EOF

nginx -t

#############################################################################
# 11. SELINUX AND FIREWALL
#############################################################################
log_info "[11/13] SELinux va firewall sozlanmoqda..."

setsebool -P httpd_can_network_connect 1 || log_warn "SELinux boolean o'rnatilmadi."
semanage fcontext -a -t httpd_sys_content_t "${APP_DIR}/static(/.*)?" 2>/dev/null || true
semanage fcontext -a -t httpd_sys_content_t "${APP_DIR}/public(/.*)?" 2>/dev/null || true
restorecon -Rv "$APP_DIR/static" "$APP_DIR/public" >/dev/null 2>&1 || true

firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload

#############################################################################
# 12. START SERVICES
#############################################################################
log_info "[12/13] Servislar ishga tushirilmoqda..."

systemctl daemon-reload
systemctl enable "gunicorn_${APP_NAME}.service" "daphne_${APP_NAME}.service"
systemctl restart mariadb redis
systemctl restart "gunicorn_${APP_NAME}.service" "daphne_${APP_NAME}.service" nginx

#############################################################################
# 13. SSL CERTIFICATE
#############################################################################
log_info "[13/13] Let's Encrypt SSL tekshirilmoqda..."

if [ -z "$DOMAIN" ] || [ "$DOMAIN" = "your-domain.com" ]; then
    log_warn "DOMAIN hali o'zgartirilmagan, SSL o'tkazib yuborildi."
    log_warn "Keyin ishga tushiring: certbot --nginx -d domen.uz -d www.domen.uz"
else
    certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" \
        --non-interactive --agree-tos -m "$EMAIL" --redirect || \
        log_warn "SSL avtomatik olinmadi. DNS domeni server IP manziliga yo'naltirilganini tekshiring."
fi

write_credentials_file

sleep 2

log_info "Service status:"
systemctl --no-pager --full status "gunicorn_${APP_NAME}.service" | grep -E "Active:|Loaded:" || true
systemctl --no-pager --full status "daphne_${APP_NAME}.service" | grep -E "Active:|Loaded:" || true
systemctl --no-pager --full status nginx.service | grep -E "Active:|Loaded:" || true
systemctl --no-pager --full status mariadb.service | grep -E "Active:|Loaded:" || true
systemctl --no-pager --full status redis.service | grep -E "Active:|Loaded:" || true

log_info "=================================================="
log_info "DEPLOYMENT COMPLETE"
log_info "=================================================="
echo "Website: http://$DOMAIN"
echo "Admin:   http://$DOMAIN/admin/"
echo "App dir: $APP_DIR"
echo "Credentials: $APP_DIR/DATABASE_CREDENTIALS.txt"
echo ""
echo "Logs:"
echo "  journalctl -u gunicorn_${APP_NAME} -n 100 -f"
echo "  journalctl -u daphne_${APP_NAME} -n 100 -f"
echo "  journalctl -u nginx -n 100 -f"
