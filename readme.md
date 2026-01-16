# Лабораторная работа №6: Контейнеризация Django-приложения

Проект представляет собой веб-приложение на Django, развернутое в Docker-контейнерах с использованием Nginx и PostgreSQL.

## Структура сервисов
* **db**: PostgreSQL 15 (Alpine)
* **web**: Django приложение (Gunicorn)
* **nginx**: Reverse-proxy сервер для статики и перенаправления запросов

## Требования
* Docker
* Docker Compose

## Установка и запуск

1. **Клонирование репозитория:**
   ```bash
   git clone https://github.com/LoopCh/web_fefu_2025
   cd web_fefu_2025
   ```

2. **Создание файла окружения:**
    ```
    DEBUG=1
    DJANGO_SECRET_KEY=твоя_секретная_строка
    DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 [::1] web <ТВОЙ_IP>
    CSRF_TRUSTED_ORIGINS=http://localhost [http://127.0.0.1](http://127.0.0.1) http://<ТВОЙ_IP>

    DB_NAME=fefu_lab_db
    DB_USER=fefu_user
    DB_PASSWORD=super_password
    DB_HOST=db
    DB_PORT=5432
    ```

3. **Запуск контейнеров:**
    ```bash
    docker compose up -d --build
    ```

4. **Создание суперпользователя (для доступа в админку):**
    ```bash
    docker compose exec web python manage.py createsuperuser
    ```

## Доступ к приложению

- Основной сайт: http://<IP-адрес>/
- Админ-панель: http://<IP-адре>/admin/


