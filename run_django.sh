#!/bin/bash

source venv/bin/activate

echo "Применение миграций..."
python manage.py makemigrations
python manage.py migrate

echo "Сбор статических файлов..."
python manage.py collectstatic --noinput

echo "Запуск Django сервера..."
python manage.py runserver 0.0.0.0:8000