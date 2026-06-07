# AlmaLinux: Django migrate va versionlarni sozlash

Bu hujjat `core/settings.py` dagi joriy sozlamalarga asoslangan:

- Django: `5.1.x`
- Python: lokal venv bo'yicha `3.12.0`
- Database: MySQL/MariaDB (`django.db.backends.mysql`)
- DB nomi: `agriculture_db`
- DB user: `agriculture_user`
- Redis: `127.0.0.1:6379`
- ASGI server: Daphne
- App: `agriculture`

Muhim: mavjud `settings.py` database, secret key, Redis va MQTT qiymatlarini `.env` dan o'qimayapti. Shuning uchun `.env` yaratishning o'zi DB ulanishini o'zgartirmaydi. Production uchun keyinroq `settings.py` ni `decouple.config()` orqali env-based qilish tavsiya qilinadi.

## 1. AlmaLinux paketlarini o'rnatish

AlmaLinux 9 uchun:

```bash
sudo dnf update -y
sudo dnf install -y epel-release
sudo dnf install -y git gcc gcc-c++ make pkgconf-pkg-config
sudo dnf install -y python3.12 python3.12-devel python3.12-pip
sudo dnf install -y mariadb-server mariadb-devel redis nginx
```

MQTT broker kerak bo'lsa:

```bash
sudo dnf install -y mosquitto mosquitto-clients
sudo systemctl enable --now mosquitto
```

Servislarni yoqish:

```bash
sudo systemctl enable --now mariadb
sudo systemctl enable --now redis
sudo systemctl enable --now nginx
```

Versiyalarni tekshirish:

```bash
python3.12 --version
mysql --version
redis-server --version
nginx -v
```

## 2. Project va virtualenv

```bash
cd /var/www
sudo git clone https://github.com/Saidmirzo/agriculture.git
sudo chown -R $USER:$USER /var/www/agriculture
cd /var/www/agriculture

python3.12 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

`mysqlclient` build bo'lishi uchun `mariadb-devel`, `gcc`, `python3.12-devel` paketlari oldindan o'rnatilgan bo'lishi shart.

Dependencies o'rnatish:

```bash
pip install -r requirements.txt
```

Tekshirish:

```bash
python -m django --version
python -c "import MySQLdb; print('mysqlclient ok')"
python -c "import channels_redis; print('channels_redis ok')"
```

## 3. Python package versiyalarini pin qilish

Hozirgi `requirements.txt` da versiyalar pin qilinmagan. Productionda bir xil natija olish uchun ishlayotgan venv ichida lock fayl yarating:

```bash
source /var/www/agriculture/venv/bin/activate
pip freeze > requirements.lock.txt
```

Keyingi deploylarda pinlangan versiyalar bilan o'rnatish:

```bash
pip install -r requirements.lock.txt
```

Lokal venvda ko'rilgan asosiy mos versiyalar:

```txt
Python==3.12.0
Django==5.1.6
djangorestframework==3.15.2
drf-spectacular==0.28.0
channels==4.2.0
channels_redis==4.2.1
daphne==4.1.2
mysqlclient==2.2.7
redis==5.2.1
gunicorn==23.0.0
sentry-sdk==2.20.0
python-decouple==3.8
python-dotenv==1.0.1
```

Agar aynan `settings.py` commentidagi Django versiyasini ushlamoqchi bo'lsangiz:

```bash
pip install "Django==5.1.4"
pip freeze > requirements.lock.txt
```

Agar lokal ishlagan versiyani productionga ko'chirmoqchi bo'lsangiz, `Django==5.1.6` bilan qoldiring.

## 4. MySQL/MariaDB database yaratish

`settings.py` dagi qiymatlar bo'yicha:

```bash
sudo mysql
```

MySQL shell ichida:

```sql
CREATE DATABASE agriculture_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'agriculture_user'@'localhost' IDENTIFIED BY 'agriculture_password';
GRANT ALL PRIVILEGES ON agriculture_db.* TO 'agriculture_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Ulanishni tekshirish:

```bash
mysql -u agriculture_user -p agriculture_db
```

Password:

```txt
agriculture_password
```

## 5. Django migration qilish

Virtualenv aktiv bo'lishi kerak:

```bash
cd /var/www/agriculture
source venv/bin/activate
```

Avval Django sozlamalarini tekshiring:

```bash
python manage.py check
```

Qaysi migrationlar borligini ko'rish:

```bash
python manage.py showmigrations
python manage.py showmigrations agriculture
```

Model o'zgargan bo'lsa yangi migration yaratish:

```bash
python manage.py makemigrations agriculture
```

Migration SQL ni oldindan ko'rish, masalan `0005` uchun:

```bash
python manage.py sqlmigrate agriculture 0005
```

Migrationlarni DB ga qo'llash:

```bash
python manage.py migrate
```

Faqat bitta app uchun:

```bash
python manage.py migrate agriculture
```

Static fayllar:

```bash
python manage.py collectstatic --noinput
```

Admin user:

```bash
python manage.py createsuperuser
```

## 6. Mavjud DB bo'lsa xavfsiz migration tartibi

Production DB ni backup qiling:

```bash
mysqldump -u agriculture_user -p agriculture_db > agriculture_db_$(date +%F_%H-%M).sql
```

Keyin:

```bash
python manage.py showmigrations
python manage.py migrate --plan
python manage.py migrate
```

Agar jadval allaqachon mavjud, lekin Django migration history bo'sh bo'lsa, birinchi deployda quyidagini ishlatish mumkin:

```bash
python manage.py migrate --fake-initial
```

Bu buyruq faqat mavjud schema migrationlarga mos bo'lsa ishlatiladi. Agar schema farq qilsa, avval DB strukturani tekshirish kerak.

## 7. Migration muammolarini diagnostika qilish

DB ulanishini Django orqali tekshirish:

```bash
python manage.py dbshell
```

Migration history:

```sql
SELECT app, name, applied FROM django_migrations ORDER BY applied;
```

Django xatolarini ko'rish:

```bash
python manage.py check --deploy
```

MySQL charset tekshirish:

```sql
SHOW VARIABLES LIKE 'character_set_database';
SHOW VARIABLES LIKE 'collation_database';
```

## 8. Redis va Channels tekshirish

`settings.py` bo'yicha Redis:

```txt
127.0.0.1:6379
```

Tekshirish:

```bash
redis-cli ping
```

Natija:

```txt
PONG
```

Python import:

```bash
python -c "from channels_redis.core import RedisChannelLayer; print('RedisChannelLayer ok')"
```

## 9. Daphne bilan ishga tushirish

Test uchun:

```bash
cd /var/www/agriculture
source venv/bin/activate
daphne -b 0.0.0.0 -p 8001 core.asgi:application
```

Oddiy Django dev server test:

```bash
python manage.py runserver 0.0.0.0:8000
```

Productionda Daphne systemd orqali yurishi kerak.

## 10. Systemd service namunasi: Daphne

Fayl:

```bash
sudo nano /etc/systemd/system/agriculture-daphne.service
```

Ichiga:

```ini
[Unit]
Description=Agriculture Daphne ASGI Service
After=network.target redis.service mariadb.service

[Service]
User=nginx
Group=nginx
WorkingDirectory=/var/www/agriculture
ExecStart=/var/www/agriculture/venv/bin/daphne -b 127.0.0.1 -p 8001 core.asgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Ishga tushirish:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now agriculture-daphne
sudo systemctl status agriculture-daphne
```

Log:

```bash
sudo journalctl -u agriculture-daphne -f
```

## 11. Har deployda ishlatiladigan qisqa tartib

```bash
cd /var/www/agriculture
git pull
source venv/bin/activate
pip install -r requirements.lock.txt
python manage.py check
python manage.py migrate --plan
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart agriculture-daphne
sudo systemctl restart nginx
```

## 12. Tavsiya: `settings.py` ni env-based qilish

Hozir production secret va DB parol kod ichida turibdi. Keyingi qadamda quyidagicha qilish yaxshi:

```python
from decouple import config

SECRET_KEY = config("DJANGO_SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="").split(",")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": config("DB_NAME", default="agriculture_db"),
        "USER": config("DB_USER", default="agriculture_user"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="3306"),
    }
}
```

`.env`:

```env
DJANGO_SECRET_KEY=change-me
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DB_NAME=agriculture_db
DB_USER=agriculture_user
DB_PASSWORD=strong-db-password
DB_HOST=localhost
DB_PORT=3306
```

Bu o'zgarishdan keyin:

```bash
python manage.py check
python manage.py migrate --plan
python manage.py migrate
sudo systemctl restart agriculture-daphne
```
