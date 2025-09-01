import os
import sys
from decimal import Decimal

import django

"""
Тестовый скрипт для проверки интеграции со Stripe
"""


# Настройка Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from materials.models import Course, Lesson
from users.models import User
from users.services import StripeService


def test_stripe_integration():
    """Тестирование интеграции со Stripe"""

    print("🧪 Тестирование интеграции со Stripe...")

    try:
        # Проверяем настройки Stripe
        from django.conf import settings

        if (
            not settings.STRIPE_SECRET_KEY
            or settings.STRIPE_SECRET_KEY == "sk_test_..."
        ):
            print("❌ STRIPE_SECRET_KEY не настроен в settings.py")
            return False

        print("✅ Настройки Stripe найдены")

        # Тестируем создание продукта
        print("\n📦 Создание тестового продукта...")
        product_data = StripeService.create_product(
            name="Тестовый курс", description="Описание тестового курса"
        )
        print(f"✅ Продукт создан: {product_data['id']}")

        # Тестируем создание цены
        print("\n💰 Создание цены...")
        price_data = StripeService.create_price(
            product_id=product_data["id"], amount=Decimal("1000.00")
        )
        print(f"✅ Цена создана: {price_data['id']}")

        # Тестируем создание сессии
        print("\n🛒 Создание сессии оплаты...")
        session_data = StripeService.create_checkout_session(
            price_id=price_data["id"],
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
            metadata={"test": "true"},
        )
        print(f"✅ Сессия создана: {session_data['id']}")
        print(f"🔗 Ссылка на оплату: {session_data['url']}")

        # Тестируем получение статуса
        print("\n📊 Проверка статуса сессии...")
        status_data = StripeService.get_session_status(session_data["id"])
        print(f"✅ Статус получен: {status_data['payment_status']}")

        print("\n🎉 Все тесты прошли успешно!")
        return True

    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return False


def test_api_endpoints():
    """Тестирование API эндпоинтов"""

    print("\n🌐 Тестирование API эндпоинтов...")

    try:
        # Проверяем, что сервер запущен
        import requests

        # Тестируем документацию
        response = requests.get("http://localhost:8000/api/schema/")
        if response.status_code == 200:
            print("✅ API Schema доступен")
        else:
            print("❌ API Schema недоступен")

        # Тестируем Swagger UI
        response = requests.get("http://localhost:8000/api/docs/")
        if response.status_code == 200:
            print("✅ Swagger UI доступен")
        else:
            print("❌ Swagger UI недоступен")

        print("\n📖 Документация доступна по адресам:")
        print("   - Swagger UI: http://localhost:8000/api/docs/")
        print("   - ReDoc: http://localhost:8000/api/redoc/")
        print("   - Schema: http://localhost:8000/api/schema/")

    except requests.exceptions.ConnectionError:
        print("❌ Сервер не запущен. Запустите: python manage.py runserver")
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")


if __name__ == "__main__":
    print("🚀 Запуск тестов интеграции...")

    # Тестируем Stripe
    stripe_success = test_stripe_integration()

    # Тестируем API
    test_api_endpoints()

    if stripe_success:
        print("\n✅ Интеграция готова к использованию!")
        print("\n📝 Следующие шаги:")
        print("1. Установите stripe: pip install stripe")
        print("2. Настройте ключи Stripe в .env файле")
        print("3. Выполните миграции: python manage.py migrate")
        print("4. Запустите сервер: python manage.py runserver")
        print("5. Откройте документацию: http://localhost:8000/api/docs/")
    else:
        print("\n❌ Интеграция требует настройки")
        sys.exit(1)
