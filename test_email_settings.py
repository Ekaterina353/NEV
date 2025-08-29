#!/usr/bin/env python
"""
Тест настроек email и DEFAULT_FROM_EMAIL
"""

import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail


def test_email_settings():
    """Тест настроек email"""
    print("🔍 Тест настроек email...")
    print("-" * 50)
    
    print("Настройки из settings.py:")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_SSL: {getattr(settings, 'EMAIL_USE_SSL', False)}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    
    print("\nПроверка переменных окружения:")
    print(f"DEFAULT_FROM_EMAIL из env: {os.getenv('DEFAULT_FROM_EMAIL', 'НЕ УСТАНОВЛЕНА')}")
    print(f"EMAIL_HOST_USER из env: {os.getenv('EMAIL_HOST_USER', 'НЕ УСТАНОВЛЕНА')}")
    
    print("\nТест отправки email...")
    try:
        # Простая проверка без реальной отправки
        if settings.DEFAULT_FROM_EMAIL and settings.EMAIL_HOST_USER:
            print("✅ Настройки email корректны")
            print(f"   from_email будет: {settings.DEFAULT_FROM_EMAIL}")
            print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        else:
            print("❌ Настройки email неполные")
            print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
            print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    test_email_settings() 