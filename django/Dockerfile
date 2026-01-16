###########
# BUILDER #
###########
FROM python:3.11 as builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 1. ОБНОВЛЕНИЕ: Добавили libpq-dev сюда, чтобы psycopg2 не падал при импорте
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc python3-dev musl-dev libpq-dev

COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

COPY . .

# 2. ОБНОВЛЕНИЕ: Исправлена команда.
# Мы не передаем DB_HOST, чтобы Django использовал SQLite (согласно нашему settings.py).
# Мы используем правильное имя переменной DJANGO_SECRET_KEY.
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

# Тут libpq-dev тоже нужен для запуска
RUN apt-get update && apt-get install -y --no-install-recommends netcat-openbsd libpq-dev && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

COPY --from=builder /usr/src/app/static $APP_HOME/static
COPY --from=builder /usr/src/app .

RUN chown -R app:app $APP_HOME

USER app

ENTRYPOINT ["/home/app/web/entrypoint.sh"]