###########
# BUILDER #
###########
FROM python:3.11 as builder

WORKDIR /usr/src/app

# Устанавливаем переменные окружения, чтобы Python не писал pyc файлы и stdout был небуферизированным
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Установка системных зависимостей для сборки (если нужно для psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev musl-dev

# Установка python зависимостей
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

# Копируем код для сборки статики
COPY . .

# Сборка статики (трюк: задаем dummy-переменные, так как базы данных на этапе сборки нет)
# Нам нужно, чтобы collectstatic отработал и положил файлы в STATIC_ROOT
RUN SECRET_KEY=dummy DB_ENGINE=django.db.backends.sqlite3 python manage.py collectstatic --noinput

#########
# FINAL #
#########
FROM python:3.11-slim

# Создаем пользователя (security best practice)
RUN mkdir -p /home/app
RUN groupadd -r app && useradd -r -g app app

# Создаем директории для приложения
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir -p $APP_HOME
RUN mkdir $APP_HOME/static
RUN mkdir $APP_HOME/media
WORKDIR $APP_HOME

# Устанавливаем netcat (для entrypoint скрипта проверки БД) и libpq (для postgres)
RUN apt-get update && apt-get install -y --no-install-recommends netcat-openbsd libpq-dev && rm -rf /var/lib/apt/lists/*

# Копируем колеса из builder и устанавливаем
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

# Копируем собранную статику и код приложения
COPY --from=builder /usr/src/app/static $APP_HOME/static
COPY --from=builder /usr/src/app .

# Меняем владельца файлов на app
RUN chown -R app:app $APP_HOME

# Переключаемся на пользователя
USER app

# Entrypoint будет добавлен позже, пока просто копируем его (если он есть в папке)
# (Сам файл создадим на шаге 6)
ENTRYPOINT ["/home/app/web/entrypoint.sh"]