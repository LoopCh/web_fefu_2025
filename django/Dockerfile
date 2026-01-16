###########
# BUILDER #
###########
FROM python:3.11 as builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем системные зависимости (нужны для сборки psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc python3-dev musl-dev libpq-dev

# Копируем requirements
COPY ./requirements.txt .

# 1. Создаем wheels (архивы пакетов) для финального образа
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Копируем код проекта
COPY . .

# Собираем статику. Теперь это сработает, т.к. Django установлен.
RUN DJANGO_SECRET_KEY=dummy-key-for-build python manage.py collectstatic --noinput

#########
# FINAL #
#########
FROM python:3.11-slim

RUN mkdir -p /home/app
RUN groupadd -r app && useradd -r -g app app

ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir -p $APP_HOME
RUN mkdir $APP_HOME/static
RUN mkdir $APP_HOME/media
WORKDIR $APP_HOME

# Устанавливаем библиотеки для рантайма (netcat для проверки порта, libpq для базы)
RUN apt-get update && apt-get install -y --no-install-recommends netcat-openbsd libpq-dev && rm -rf /var/lib/apt/lists/*

# Копируем wheels из builder и устанавливаем их
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

# Копируем уже собранную статику из builder в папку static
COPY --from=builder /usr/src/app/static $APP_HOME/static

# Копируем код приложения
COPY --from=builder /usr/src/app .

# Меняем права
RUN chown -R app:app $APP_HOME

# Переключаем пользователя
USER app

# Entrypoint
ENTRYPOINT ["/home/app/web/entrypoint.sh"]