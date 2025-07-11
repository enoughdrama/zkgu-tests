# Management System

### Установка

```bash
# 1. Клонировать проект
git clone https://github.com/enoughdrama/zkgu-tests
cd zkgu_project

# 2. Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # На macOS/Linux
# venv\Scripts\activate    # На Windows

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Настроить базу данных
python manage.py migrate

# 5. Запустить сервер
python manage.py runserver
```

### Первый запуск

1. Откройте браузер: http://localhost:8000/api/v1/manage/
2. Добавьте первую персону через форму слева
3. Проверьте что данные сохранились в списке справа

---

## Основные функции

### 1. Добавление персон

**Через веб-интерфейс:**
1. Заполните форму в левой панели:
   - **ID Record** (обязательно) - уникальный идентификатор
   - **Last Name** (обязательно) - фамилия
   - **First Name** (опционально) - имя
   - **Middle Name** (опционально) - отчество
2. Нажмите кнопку "Add Person"
3. Персона появится в списке справа

**Через API:**
```bash
curl -X POST http://localhost:8000/api/v1/debug/ \
  -H "Content-Type: application/json" \
  -d '{
    "ID_REC": "USR001",
    "LASTNAME": "Иванов", 
    "FIRSTNAME": "Иван",
    "MIDNAME": "Иванович"
  }'
```

### 2. Редактирование персон

**Через веб-интерфейс:**
1. Наведите курсор на нужную персону в списке
2. Нажмите кнопку редактирования (📝)
3. Измените данные в модальном окне
4. Нажмите "Save Changes"

**Через API:**
```bash
curl -X PATCH http://localhost:8000/api/v1/update/USR001/ \
  -H "Content-Type: application/json" \
  -d '{
    "LASTNAME": "Петров",
    "FIRSTNAME": "Петр"
  }'
```

### 3. Удаление персон

**Через веб-интерфейс:**
1. Наведите курсор на персону
2. Нажмите кнопку удаления (🗑️)
3. Подтвердите удаление

**Через API:**
```bash
curl -X GET http://localhost:8000/api/v1/delete/USR001/
```

### 4. Поиск и фильтрация

**В веб-интерфейсе:**
- Используйте поле поиска в правом верхнем углу
- Поиск работает по всем полям: ID, фамилии, имени, отчеству
- Результаты обновляются в реальном времени

**Примеры поиска:**
- `USR001` - поиск по ID
- `Иванов` - поиск по фамилии
- `Иван` - поиск по имени

---

## 🔌 API Документация

### Базовые endpoints

| Метод | URL | Описание |
|-------|-----|----------|
| `GET` | `/api/v1/debug/` | Получить список всех персон |
| `POST` | `/api/v1/debug/` | Создать новую персону |
| `GET` | `/api/v1/person/{id}/` | Получить данные персоны |
| `PATCH` | `/api/v1/update/{id}/` | Обновить персону |
| `GET` | `/api/v1/delete/{id}/` | Удалить персону |
| `GET` | `/api/v1/updates/` | Проверить обновления (polling) |

### Структура данных

**Объект персоны:**
```json
{
  "ID_REC": "USR001",
  "LASTNAME": "Иванов",
  "FIRSTNAME": "Иван", 
  "MIDNAME": "Иванович",
  "DELETION_MARK": 0,
  "last_update": "2025-07-11T10:30:00Z",
  "created_at": "2025-07-11T10:00:00Z"
}
```

**Ответ API:**
```json
{
  "status": "success",
  "count": 1,
  "results": [...],
  "data": {...}
}
```

### Примеры запросов

**Получить все персоны:**
```bash
curl http://localhost:8000/api/v1/debug/
```

**Создать персону:**
```bash
curl -X POST http://localhost:8000/api/v1/debug/ \
  -H "Content-Type: application/json" \
  -d '{
    "ID_REC": "USR002",
    "LASTNAME": "Сидоров",
    "FIRSTNAME": "Сидор"
  }'
```

**Обновить персону:**
```bash
curl -X PATCH http://localhost:8000/api/v1/update/USR002/ \
  -H "Content-Type: application/json" \
  -d '{"FIRSTNAME": "Сидорович"}'
```

**Получить конкретную персону:**
```bash
curl http://localhost:8000/api/v1/person/USR002/
```

---

## 🔧 Настройки и конфигурация

### Переменные окружения

Создайте файл `.env`:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
```

### Настройки поллинга

По умолчанию система проверяет обновления каждые 2 секунды. Для изменения интервала отредактируйте в HTML:

```javascript
// Изменить интервал на 5 секунд
pollingInterval = setInterval(checkForUpdates, 5000);
```

### Настройки WebSocket

```bash
# Установить дополнительные пакеты
pip install channels[daphne] channels-redis

# Запустить с WebSocket поддержкой
daphne -p 8000 zkgu_project.asgi:application
```