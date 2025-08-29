# Примеры использования API

## Аутентификация

### Получение JWT токена
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Обновление токена
```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "your_refresh_token_here"
  }'
```

## Курсы

### Создание курса
```bash
curl -X POST http://localhost:8000/api/courses/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Python для начинающих",
    "description": "Базовый курс по Python"
  }'
```

### Получение списка курсов
```bash
curl -X GET http://localhost:8000/api/courses/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Подписки

### Добавление/удаление подписки
```bash
curl -X POST http://localhost:8000/api/subscriptions/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "course_id": 1
  }'
```

**Ответы:**
- `201` - Подписка создана
- `204` - Подписка удалена

## Stripe Платежи

### Создание платежа для курса
```bash
curl -X POST http://localhost:8000/api/payments/stripe/create/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "course_id": 1,
    "amount": 5000.00
  }'
```

**Ответ:**
```json
{
  "payment_id": 1,
  "checkout_url": "https://checkout.stripe.com/pay/cs_test_...",
  "session_id": "cs_test_..."
}
```

### Создание платежа для урока
```bash
curl -X POST http://localhost:8000/api/payments/stripe/create/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "lesson_id": 1,
    "amount": 1000.00
  }'
```

### Проверка статуса платежа
```bash
curl -X GET "http://localhost:8000/api/payments/stripe/status/?session_id=cs_test_..." \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Ответ:**
```json
{
  "session_id": "cs_test_...",
  "payment_status": "paid",
  "status": "complete",
  "amount_total": 500000,
  "currency": "rub",
  "customer_email": "customer@example.com"
}
```

## Платежи

### Получение списка платежей
```bash
curl -X GET http://localhost:8000/api/payments/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Фильтрация платежей
```bash
# По курсу
curl -X GET "http://localhost:8000/api/payments/?course=1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# По способу оплаты
curl -X GET "http://localhost:8000/api/payments/?payment_method=stripe" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Сортировка по дате
curl -X GET "http://localhost:8000/api/payments/?ordering=-payment_date" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Статистика платежей
```bash
curl -X GET http://localhost:8000/api/users/me/payments/stats/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Ответ:**
```json
{
  "total_amount": 15000.00,
  "by_method": [
    {
      "payment_method": "stripe",
      "total": 10000.00,
      "count": 2
    },
    {
      "payment_method": "cash",
      "total": 5000.00,
      "count": 1
    }
  ]
}
```

## Пользователи

### Регистрация пользователя
```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "password123",
    "first_name": "Иван",
    "last_name": "Иванов",
    "phone": "+79001234567",
    "city": "Москва"
  }'
```

### Получение профиля
```bash
curl -X GET http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Обновление профиля
```bash
curl -X PUT http://localhost:8000/api/users/me/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Петр",
    "city": "Санкт-Петербург"
  }'
```

## Тестирование Stripe

### Тестовые карты

Для тестирования используйте следующие номера карт:

| Номер карты | Результат | Описание |
|-------------|-----------|----------|
| `4242 4242 4242 4242` | ✅ Успех | Стандартная карта |
| `4000 0000 0000 9995` | ❌ Ошибка | Недостаточно средств |
| `4000 0000 0000 0002` | ❌ Ошибка | Карта отклонена |
| `4000 0000 0000 3220` | ⚠️ 3D Secure | Требует аутентификации |

**Любая будущая дата и CVC код (например, 12/25 и 123)**

### Полный процесс оплаты

1. **Создание платежа:**
```bash
curl -X POST http://localhost:8000/api/payments/stripe/create/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "course_id": 1,
    "amount": 5000.00
  }'
```

2. **Переход по ссылке оплаты** (из ответа выше)

3. **Ввод тестовых данных карты:**
   - Номер: `4242 4242 4242 4242`
   - Дата: `12/25`
   - CVC: `123`

4. **Проверка статуса:**
```bash
curl -X GET "http://localhost:8000/api/payments/stripe/status/?session_id=cs_test_..." \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Обработка ошибок

### Примеры ошибок

**Неверный токен:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Недостаточно данных:**
```json
{
  "error": "Сумма оплаты обязательна"
}
```

**Курс не найден:**
```json
{
  "detail": "Not found."
}
```

**Ошибка Stripe:**
```json
{
  "error": "Ошибка создания продукта в Stripe: Invalid API key provided"
}
``` 