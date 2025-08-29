#!/usr/bin/env python
"""
Простой тест для проверки работы Celery без email
"""

import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from materials.tasks import simple_test_task


def test_simple_celery():
    """Простой тест Celery без email"""
    print("🧪 Простой тест Celery...")
    print("-" * 50)
    
    try:
        print("1. Отправка простой задачи...")
        result = simple_test_task.delay()
        print(f"   Task ID: {result.id}")
        
        # Получаем результат
        task_result = result.get(timeout=10)
        print(f"   Результат: {task_result}")
        print("   ✅ Celery работает!")
        
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        print("\n🔧 Устранение неполадок:")
        print("1. Убедитесь, что Redis запущен: redis-cli ping")
        print("2. Запустите Celery worker:")
        print("   celery -A config worker --pool=solo -l info")
        print("3. В отдельном терминале запустите этот тест")


if __name__ == "__main__":
    print("🚀 Запуск простого теста Celery...")
    test_simple_celery() 