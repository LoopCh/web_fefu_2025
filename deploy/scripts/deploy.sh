#!/bin/bash
set -e

PROJECT_NAME="fefu_lab"
PROJECT_DIR="/var/www/$PROJECT_NAME"
REPO_URL="https://github.com/LoopCh/web_fefu_2025"
DB_NAME="fefu_lab_db"
DB_USER="fefu_user"
DB_PASSWORD="admin"

echo "=== Деплой Django приложения ==="

# 1. Установка необходимых пакетов
echo "[1/10] Установка системных пакетов..."
sudo apt update
sudo apt install -y python3-venv python3-dev libpq-dev postgresql postgresql-contrib nginx curl git

# 2. Настройка PostgreSQL
echo "[2/10] Настройка PostgreSQL..."
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
sudo -u postgres psql <<EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
ALTER ROLE $DB_USER SET client_encoding TO 'utf8';
ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';
ALTER ROLE $DB_USER SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

# 3. Клонирование репозитория
echo "[3/10] Клонирование репозитория..."
if [ -d "$PROJECT_DIR" ]; then
    sudo rm -rf "$PROJECT_DIR"
fi
sudo git clone "$REPO_URL" "$PROJECT_DIR"

# 4. Создание виртуального окружения
echo "[4/10] Создание виртуального окружения..."
sudo python3 -m venv "$PROJECT_DIR/venv"

# 5. Установка Python зависимостей
echo "[5/10] Установка зависимостей..."
sudo "$PROJECT_DIR/venv/bin/pip" install --upgrade pip
sudo "$PROJECT_DIR/venv/bin/pip" install -r "$PROJECT_DIR/requirements.txt"

# 6. Миграция базы данных
echo "[6/10] Применение миграций..."
cd "$PROJECT_DIR"
sudo DJANGO_ENV=production \
     DB_NAME="$DB_NAME" \
     DB_USER="$DB_USER" \
     DB_PASSWORD="$DB_PASSWORD" \
     DB_HOST=localhost \
     DB_PORT=5432 \
     DJANGO_SECRET_KEY=your-secret-key-here-change-this \
     "$PROJECT_DIR/venv/bin/python" manage.py migrate --settings=web_2025.settings

sudo DJANGO_ENV=production \
     DB_NAME="$DB_NAME" \
     DB_USER="$DB_USER" \
     DB_PASSWORD="$DB_PASSWORD" \
     DB_HOST=localhost \
     DB_PORT=5432 \
     DJANGO_SECRET_KEY=your-secret-key-here-change-this \
     "$PROJECT_DIR/venv/bin/python" manage.py loaddata data.json --settings=web_2025.settings

sudo DJANGO_ENV=production \
     DB_NAME="$DB_NAME" \
     DB_USER="$DB_USER" \
     DB_PASSWORD="$DB_PASSWORD" \
     DB_HOST=localhost \
     DB_PORT=5432 \
     DJANGO_SECRET_KEY=your-secret-key-here-change-this \
     "$PROJECT_DIR/venv/bin/python" manage.py collectstatic --no-input --settings=web_2025.settings

# 7. Настройка директорий и прав
echo "[7/10] Настройка директорий..."
sudo mkdir -p "$PROJECT_DIR/static" "$PROJECT_DIR/media" /var/log/gunicorn
sudo chown -R www-data:www-data "$PROJECT_DIR" /var/log/gunicorn
sudo chmod -R 755 "$PROJECT_DIR"

# 8. Настройка Nginx
echo "[8/10] Настройка Nginx..."
sudo cp "$PROJECT_DIR/deploy/nginx/fefu_lab.conf" /etc/nginx/sites-available/
sudo ln -sf /etc/nginx/sites-available/fefu_lab.conf /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t

# 9. Настройка и запуск Gunicorn 
echo "[9/10] Настройка Gunicorn..."
sudo cp "$PROJECT_DIR/deploy/systemd/gunicorn.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
sudo systemctl enable gunicorn
sudo systemctl restart nginx
sudo systemctl enable nginx

# 10. Проверка работоспособности
echo "[10/10] Проверка доступности приложения..."
sleep 5

if curl -s -o /dev/null -w "%{http_code}" http://localhost:80 | grep -q "200\|301\|302"; then
    echo ""
    echo "=== ✓ ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО! ==="
    echo "Приложение доступно на http://localhost:80"
    echo ""
    echo "Статус сервисов:"
    sudo systemctl status gunicorn --no-pager -l
    sudo systemctl status nginx --no-pager -l
else
    echo ""
    echo "=== ✗ ОШИБКА: Приложение недоступно ==="
    echo "Проверьте логи:"
    echo "  sudo journalctl -u gunicorn -n 50"
    echo "  sudo tail -f /var/log/gunicorn/error.log"
    exit 1
fi
