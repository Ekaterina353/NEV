#!/usr/bin/env python
"""
Скрипт для тестирования работы Celery и асинхронной рассылки email
"""

import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from materials.tasks import test_email_task, send_course_update_email


def test_celery_email():
    """Тестирование отправки email через Celery"""
    print("🧪 Тестирование асинхронной рассылки email...")
    
    # Тестовая задача
    print("1. Отправка тестового email...")
    try:
        result = test_email_task.delay()
        print(f"   Task ID: {result.id}")
        
        # Получаем результат
        task_result = result.get(timeout=30)
        print(f"   Результат: {task_result}")
    except Exception as e:
        print(f"   Ошибка: {e}")
        print("   Возможные причины:")
        print("   - Celery worker не запущен")
        print("   - Redis не запущен")
        print("   - Неправильные настройки email")
    
    # Тест рассылки подписчикам
    print("\n2. Тест рассылки подписчикам курса...")
    try:
        result2 = send_course_update_email.delay(
            user_email="test@example.com",
            course_name="Тестовый курс",
            material_title="Новый урок"
        )
        print(f"   Task ID: {result2.id}")
        
        task_result2 = result2.get(timeout=30)
        print(f"   Результат: {task_result2}")
    except Exception as e:
        print(f"   Ошибка: {e}")


if __name__ == "__main__":
    print("🚀 Запуск тестирования Celery...")
    print("Убедитесь, что Redis запущен и Celery worker работает!")
    print("-" * 50)
    
    test_celery_email()
    
    print("-" * 50)
    print("✅ Тестирование завершено!")
    print("\nДля запуска вручную:")
    print("1. Запустите Redis: redis-server")
    print("2. Запустите Celery worker: celery -A config worker --pool=solo -l info")
    print("3. Запустите этот скрипт: python test_celery.py")
    print("\nПримечание: На Windows используйте --pool=solo для избежания ошибок!") 