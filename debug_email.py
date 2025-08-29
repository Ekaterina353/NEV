#!/usr/bin/env python
"""
Отладочный скрипт для проверки настроек email
"""

import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings


def debug_email_settings():
    """Проверка настроек email"""
    print("🔍 Проверка настроек email...")
    print("-" * 50)
    
    # Проверяем переменные окружения
    print("Переменные окружения:")
    print(f"EMAIL_HOST: {os.getenv('EMAIL_HOST', 'НЕ УСТАНОВЛЕНА')}")
    print(f"EMAIL_PORT: {os.getenv('EMAIL_PORT', 'НЕ УСТАНОВЛЕНА')}")
    print(f"EMAIL_USE_TLS: {os.getenv('EMAIL_USE_TLS', 'НЕ УСТАНОВЛЕНА')}")
    print(f"EMAIL_HOST_USER: {os.getenv('EMAIL_HOST_USER', 'НЕ УСТАНОВЛЕНА')}")
    print(f"EMAIL_HOST_PASSWORD: {'*' * len(os.getenv('EMAIL_HOST_PASSWORD', '')) if os.getenv('EMAIL_HOST_PASSWORD') else 'НЕ УСТАНОВЛЕНА'}")
    print(f"DEFAULT_FROM_EMAIL: {os.getenv('DEFAULT_FROM_EMAIL', 'НЕ УСТАНОВЛЕНА')}")
    
    print("\nНастройки Django:")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_USE_SSL: {getattr(settings, 'EMAIL_USE_SSL', False)}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'ПУСТО'}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    print("\nПроверка .env файла:")
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        print(f"✅ Файл .env найден: {env_file}")
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    if 'PASSWORD' in key:
                        print(f"   {key}: {'*' * len(value)}")
                    else:
                        print(f"   {key}: {value}")
    else:
        print(f"❌ Файл .env не найден: {env_file}")
    
    print("\nРекомендации:")
    if not settings.EMAIL_HOST_USER:
        print("❌ EMAIL_HOST_USER не установлен")
    if not settings.EMAIL_HOST_PASSWORD:
        print("❌ EMAIL_HOST_PASSWORD не установлен")
    if not settings.DEFAULT_FROM_EMAIL:
        print("❌ DEFAULT_FROM_EMAIL не установлен")
    
    if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD and settings.DEFAULT_FROM_EMAIL:
        print("✅ Все необходимые настройки email установлены")


if __name__ == "__main__":
    debug_email_settings() 