#!/bin/bash

echo "starting..."
source venv/bin/activate

echo "1. Проверка базовых тестов моделей..."
python manage.py test zkgu_persons.tests.ZkguPersonModelTest --verbosity=1

echo "2. Проверка тестов API..."
python manage.py test zkgu_persons.tests.PersonAPITest --verbosity=1

echo "3. Проверка тестов аутентификации..."
python manage.py test zkgu_persons.tests.TokenAuthenticationTest --verbosity=1

echo "4. Запуск интеграционных тестов..."
python manage.py test test_integration --verbosity=1

echo "5. Запуск всех тестов..."
python manage.py test --verbosity=2

echo "=== Тесты завершены ==="