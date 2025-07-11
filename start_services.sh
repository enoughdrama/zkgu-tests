#!/bin/bash

echo "Запуск сервисов для zkgu_project..."

echo "Запуск Redis..."
brew services start redis

echo "Запуск RabbitMQ..."
brew services start rabbitmq

echo "Ожидание запуска сервисов..."
sleep 5

echo "Проверка статуса Redis..."
redis-cli ping

echo "Проверка статуса RabbitMQ..."
curl -s http://localhost:15672 > /dev/null && echo "RabbitMQ Management доступен" || echo "RabbitMQ Management недоступен"

echo "Сервисы запущены!"