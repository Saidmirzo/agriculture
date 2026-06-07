# Agriculture Backend: domainsiz Nginx + service deploy

Bu hujjat serverda domen ishlatmasdan, IP orqali Django API va WebSocketlarni ishga tushirish uchun. Migrate allaqachon qilingan deb olinadi.

## 1. Arxitektura

```text
Client
  |
  | http://SERVER_IP/
  v
Nginx :80
  |-- /static/ va /media/  -> fayldan beriladi
  |-- /ws/                 -> Daphne 127.0.0.1:8001
  `-- qolgan hammasi       -> Gunicorn 127.0.0.1:8000

Redis 127.0.0.1:6379 -> Django Channels group/message layer
DB                   -> migrate qilingan mavjud database
```

Project endpointlari:

| Turi | URL |
| --- | --- |
| Admin | `http://SERVER_IP/admin/` |
| Swagger | `http://SERVER_IP/swagger/` |
| API schema | `http://SERVER_IP/api/schema/` |
| Device status | `http://SERVER_IP/api/devices/status/` |
| Device CRUD/list | `http://SERVER_IP/api/devices/` |
| Device data | `http://SERVER_IP/api/devices/<device_id>/data/` |
| Send command | `http://SERVER_IP/api/send-event/` |
| Upload image | `http://SERVER_IP/api/send-image/` |
| Upload logs | `http://SERVER_IP/api/upload-logs/` |
| Logs page | `http://SERVER_IP/api/logs/` |
| Real-time logs page | `http://SERVER_IP/api/real-logs/` |
| Device WebSocket | `ws://SERVER_IP/ws/device/<device_id>/` |
| Real-time logs WebSocket | `ws://SERVER_IP/ws/device-logs/` |

## 2. Server paketlari

AlmaLinux/Rocky/RHEL uchun:

```bash
sudo dnf install -y epel-release
sudo dnf install -y git gcc make nginx redis python3.11 python3.11-devel python3.11-pip policycoreutils-python-utils firewalld
```

Agar database MariaDB/MySQL bo'lsa:

```bash
sudo dnf install -y mariadb-server mariadb-devel
sudo systemctl enable --now mariadb
```

Redis va Nginxni yoqing:

```bash
sudo systemctl enable --now redis nginx firewalld
redis-cli ping
```

`redis-cli ping` javobi `PONG` bo'lishi kerak.

## 3. Project joylashuvi

Standart path:

```bash
APP_DIR=/var/www/agriculture
APP_USER=nginx
APP_GROUP=nginx
```

Kod serverda shu katalogda turishi tavsiya qilinadi:

```bash
sudo mkdir -p /var/www/agriculture
sudo chown -R nginx:nginx /var/www/agriculture
```

Repository allaqachon shu joyga qo'yilgan bo'lsa, keyingi qadamga o'ting. Aks holda kodni ko'chiring yoki clone qiling.

## 4. Virtual environment va dependencylar

```bash
cd /var/www/agriculture
sudo -u nginx python3.11 -m venv venv
sudo -u nginx /var/www/agriculture/venv/bin/python -m pip install --upgrade pip setuptools wheel
sudo -u nginx /var/www/agriculture/venv/bin/pip install -r requirements.txt
```

Static fayllarni yig'ing:

```bash
cd /var/www/agriculture
sudo -u nginx /var/www/agriculture/venv/bin/python manage.py collectstatic --noinput
```

Migrate sizda qilingan. Agar qayta kerak bo'lsa:

```bash
cd /var/www/agriculture
sudo -u nginx /var/www/agriculture/venv/bin/python manage.py migrate --noinput
```

## 5. `.env` namunasi

`/var/www/agriculture/.env`:

```env
DEBUG=False
DATABASE_NAME=db.sqlite3
```

Hozirgi `core/settings.py` sqlite ishlatadi va `DATABASE_NAME` default qiymati `db.sqlite3`. Agar MariaDB/MySQL ga o'tkazilgan bo'lsa, settingsdagi MySQL qismi yoqilgan bo'lishi kerak.

Domainsiz/IP orqali ishlatishda hozirgi settingsdagi `ALLOWED_HOSTS = ['*']` APIga ruxsat beradi. Production uchun keyinroq `SERVER_IP` bilan cheklash yaxshiroq.

## 6. Gunicorn service

`/etc/systemd/system/gunicorn_agriculture.service` faylini yarating:

```ini
[Unit]
Description=Gunicorn service for agriculture HTTP API
After=network.target redis.service
Requires=redis.service

[Service]
Type=simple
User=nginx
Group=nginx
WorkingDirectory=/var/www/agriculture
Environment="PATH=/var/www/agriculture/venv/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=/var/www/agriculture/venv/bin/gunicorn \
    --workers 3 \
    --worker-class sync \
    --bind 127.0.0.1:8000 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    core.wsgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Gunicorn faqat HTTP API/admin/static bo'lmagan requestlar uchun. WebSocket uchun Gunicorn emas, Daphne ishlaydi.

## 7. Daphne service

`/etc/systemd/system/daphne_agriculture.service` faylini yarating:

```ini
[Unit]
Description=Daphne ASGI service for agriculture WebSockets
After=network.target redis.service
Requires=redis.service

[Service]
Type=simple
User=nginx
Group=nginx
WorkingDirectory=/var/www/agriculture
Environment="PATH=/var/www/agriculture/venv/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=/var/www/agriculture/venv/bin/daphne -b 127.0.0.1 -p 8001 core.asgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Daphne `core.asgi:application` ni ishlatadi. Shu ASGI config `/ws/device/<device_id>/` va `/ws/device-logs/` routelarni ulaydi.

## 8. Services start

```bash
sudo systemctl daemon-reload
sudo systemctl enable gunicorn_agriculture daphne_agriculture
sudo systemctl restart gunicorn_agriculture daphne_agriculture
sudo systemctl status gunicorn_agriculture --no-pager
sudo systemctl status daphne_agriculture --no-pager
```

Loglar:

```bash
sudo journalctl -u gunicorn_agriculture -n 100 -f
sudo journalctl -u daphne_agriculture -n 100 -f
```

## 9. Nginx domainsiz config

`/etc/nginx/conf.d/agriculture.conf`:

```nginx
upstream agriculture_gunicorn {
    server 127.0.0.1:8000;
}

upstream agriculture_daphne {
    server 127.0.0.1:8001;
}

server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    client_max_body_size 20M;

    location /static/ {
        alias /var/www/agriculture/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/agriculture/public/;
        expires 7d;
    }

    location /ws/ {
        proxy_pass http://agriculture_daphne;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }

    location / {
        proxy_pass http://agriculture_gunicorn;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

Agar Nginx default config bilan konflikt bersa, default serverni o'chiring yoki undagi `default_server` ni olib tashlang.

Tekshirish va restart:

```bash
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl status nginx --no-pager
```

## 10. Firewall va SELinux

```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload
```

SELinux yoqilgan bo'lsa, Nginx ichki `127.0.0.1:8000/8001` ga proxy qila olishi uchun:

```bash
sudo setsebool -P httpd_can_network_connect 1
sudo semanage fcontext -a -t httpd_sys_content_t "/var/www/agriculture/static(/.*)?"
sudo semanage fcontext -a -t httpd_sys_content_t "/var/www/agriculture/public(/.*)?"
sudo restorecon -Rv /var/www/agriculture/static /var/www/agriculture/public
```

## 11. API test

Server IP ni kiriting:

```bash
SERVER_IP=1.2.3.4
curl -i "http://$SERVER_IP/api/devices/status/"
curl -i "http://$SERVER_IP/swagger/"
```

Device yaratish:

```bash
curl -i -X POST "http://$SERVER_IP/api/devices/" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"test-device-1","name":"Test device"}'
```

Command yuborish:

```bash
curl -i -X POST "http://$SERVER_IP/api/send-event/" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"test-device-1","command":"ping","command_string":"hello"}'
```

Bu command faqat device websocket orqali online bo'lsa yuboriladi.

## 12. WebSocket test

`websocat` bo'lsa:

```bash
websocat "ws://SERVER_IP/ws/device/test-device-1/"
```

Ulanganidan keyin boshqa terminaldan command yuboring:

```bash
curl -i -X POST "http://SERVER_IP/api/send-event/" \
  -H "Content-Type: application/json" \
  -d '{"device_id":"test-device-1","command":"capture_image","command_string":"now"}'
```

WebSocket terminalida shunga o'xshash JSON kelishi kerak:

```json
{"command":"capture_image","command_string":"now"}
```

Real-time logs socket:

```bash
websocat "ws://SERVER_IP/ws/device-logs/"
```

Brauzer orqali ham tekshirish mumkin:

```text
http://SERVER_IP/api/real-logs/
```

Bu sahifadagi JavaScript websocketni avtomatik `ws://SERVER_IP/ws/device-logs/` ga ulaydi.

## 13. Service boshqarish

Status:

```bash
sudo systemctl status gunicorn_agriculture daphne_agriculture nginx redis --no-pager
```

Restart:

```bash
sudo systemctl restart gunicorn_agriculture daphne_agriculture nginx
```

Stop/start:

```bash
sudo systemctl stop gunicorn_agriculture daphne_agriculture
sudo systemctl start gunicorn_agriculture daphne_agriculture
```

Loglar:

```bash
sudo journalctl -u gunicorn_agriculture -n 100 -f
sudo journalctl -u daphne_agriculture -n 100 -f
sudo journalctl -u nginx -n 100 -f
sudo tail -f /var/log/nginx/error.log
```

## 14. Update tartibi

Kod yangilangandan keyin:

```bash
cd /var/www/agriculture
sudo -u nginx git pull origin main
sudo -u nginx /var/www/agriculture/venv/bin/pip install -r requirements.txt
sudo -u nginx /var/www/agriculture/venv/bin/python manage.py migrate --noinput
sudo -u nginx /var/www/agriculture/venv/bin/python manage.py collectstatic --noinput
sudo systemctl restart gunicorn_agriculture daphne_agriculture nginx
```

## 15. Troubleshooting

502 Bad Gateway:

```bash
sudo systemctl status gunicorn_agriculture daphne_agriculture --no-pager
sudo journalctl -u gunicorn_agriculture -n 100 --no-pager
sudo journalctl -u daphne_agriculture -n 100 --no-pager
sudo nginx -t
```

WebSocket ulanmasa:

```bash
sudo journalctl -u daphne_agriculture -n 100 -f
redis-cli ping
curl -i -H "Connection: Upgrade" -H "Upgrade: websocket" "http://SERVER_IP/ws/device/test-device-1/"
```

Expected: oddiy `curl` to'liq websocket client emas, lekin Nginx requestni Daphne tomonga o'tkazayotganini loglardan ko'rasiz. Real test uchun `websocat` yoki device client ishlating.

Static/media chiqmasa:

```bash
ls -la /var/www/agriculture/static
ls -la /var/www/agriculture/public
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

Permission xatosi:

```bash
sudo chown -R nginx:nginx /var/www/agriculture
sudo restorecon -Rv /var/www/agriculture/static /var/www/agriculture/public
```

Redis xatosi:

```bash
sudo systemctl status redis --no-pager
redis-cli ping
```

## 16. Yakuniy checklist

- `redis-cli ping` -> `PONG`
- `sudo systemctl status gunicorn_agriculture` -> `active`
- `sudo systemctl status daphne_agriculture` -> `active`
- `sudo nginx -t` -> `successful`
- `http://SERVER_IP/api/devices/status/` javob qaytaradi
- `http://SERVER_IP/swagger/` ochiladi
- `ws://SERVER_IP/ws/device/<device_id>/` ulanadi
- `http://SERVER_IP/api/real-logs/` websocket error bermaydi

