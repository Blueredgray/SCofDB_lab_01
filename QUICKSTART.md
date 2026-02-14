# Быстрый старт

## Запуск проекта

```bash
docker-compose up --build
```

Или в detached режиме:
```bash
docker-compose up -d --build
```

## Доступ к приложению

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8080
- **PostgreSQL**: localhost:5432

## Проверка работы

```bash
# Проверить здоровье backend
curl http://localhost:8080/health

# Остановить контейнеры
docker-compose down
```

## Что работает из коробки

✅ Frontend отображается и загружается
✅ Backend запускается
✅ База данных инициализируется
✅ API endpoints доступны

## Что НЕ работает (и что нужно реализовать)

❌ Создание пользователей — `NotImplementedError: TODO: Реализовать UserService.register`
❌ Создание заказов — `NotImplementedError`
❌ Все остальные операции — `NotImplementedError`

Когда вы откроете http://localhost:5173, вы увидите интерфейс, но при попытке создать пользователя получите ошибку. Это нормально! Ваша задача — реализовать TODO в коде.

## Тестирование

```bash
cd backend
export PYTHONPATH=$(pwd)

# Запустить доменные тесты
pytest app/tests/test_domain.py -v

# Запустить критический тест на двойную оплату
pytest app/tests/test_domain.py::TestCriticalPaymentInvariant -v
```
