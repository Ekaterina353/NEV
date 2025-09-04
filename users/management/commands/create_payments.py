import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand

from materials.models import Course, Lesson
from users.models import Payment, User


class Command(BaseCommand):
    help = "Создает тестовые данные для модели Payment"

    def handle(self, *args, **kwargs):
        self.stdout.write("Начинаем добавление данных...")

        # Получаем тестового пользователя
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR("Пользователь не найден"))
            return

        # Получаем курс и урок
        course = Course.objects.first()
        lesson = Lesson.objects.first()

        if not course or not lesson:
            self.stdout.write(self.style.ERROR("Курс или урок не найдены"))
            return

        # Создаем платежи
        payments = [
            {
                "user": user,
                "course": course,
                "lesson": None,
                "amount": Decimal("1000.00"),
                "method": "transfer",
            },
            {
                "user": user,
                "course": None,
                "lesson": lesson,
                "amount": Decimal("200.00"),
                "method": "cash",
            },
        ]

        for data in payments:
            Payment.objects.create(**data)

        self.stdout.write(self.style.SUCCESS("Данные успешно добавлены!"))
