#!/bin/bash

# Если база данных еще не готова...
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    # Цикл ожидания доступности хоста и порта
    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Выполняем миграции при каждом запуске (можно убрать в продакшене, но для лабы удобно)
python manage.py migrate

# Запускаем команду, переданную в аргументах (gunicorn)
exec "$@"