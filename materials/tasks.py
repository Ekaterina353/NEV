from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task
def simple_test_task():
    """Простая тестовая задача без email"""
    return "Celery работает! Простая задача выполнена успешно."


@shared_task
def send_course_update_email(user_email, course_name, material_title):
    try:
        # Проверяем настройки email
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            error_msg = f"Email настройки неполные: EMAIL_HOST_USER={bool(settings.EMAIL_HOST_USER)}, EMAIL_HOST_PASSWORD={bool(settings.EMAIL_HOST_PASSWORD)}"
            logger.error(error_msg)
            return error_msg
        
        send_mail(
            subject=f'Обновление в курсе {course_name}',
            message=f'В курсе "{course_name}" появился новый материал: {material_title}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
        )
        return f"Email отправлен успешно на {user_email}"
    except Exception as e:
        error_msg = f"Ошибка отправки email: {str(e)}"
        logger.error(error_msg)
        return error_msg


@shared_task
def test_email_task():
    """Тестовая задача для проверки работы Celery и отправки email"""
    try:
        # Проверяем настройки email
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            error_msg = f"Email настройки неполные: EMAIL_HOST_USER={bool(settings.EMAIL_HOST_USER)}, EMAIL_HOST_PASSWORD={bool(settings.EMAIL_HOST_PASSWORD)}"
            logger.error(error_msg)
            return error_msg
        
        send_mail(
            subject='Тестовая рассылка от Django REST Framework',
            message='Это тестовое письмо для проверки работы асинхронной рассылки через Celery.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],  # отправляем на тот же адрес
        )
        return "Email отправлен успешно!"
    except Exception as e:
        error_msg = f"Ошибка отправки email: {str(e)}"
        logger.error(error_msg)
        return error_msg
