import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from materials.models import Course, Lesson
from users.models import Payment

User = get_user_model()


class Command(BaseCommand):
    help = "Creates initial test data"

    def handle(self, *args, **options):
        # Создаем группы
        moderator_group, _ = Group.objects.get_or_create(name="moderators")
        student_group, _ = Group.objects.get_or_create(name="students")

        # Создаем пользователей
        admin_user = User.objects.create_superuser(
            email="admin@example.com",
            password="admin123",
            first_name="Admin",
            last_name="User",
        )

        test_user = User.objects.create_user(
            email="user@example.com",
            password="user123",
            first_name="Test",
            last_name="User",
        )
        test_user.groups.add(student_group)

        # Создаем курсы
        course = Course.objects.create(
            name="Основы Python",
            description="Базовый курс по программированию на Python",
            owner=test_user,
        )

        # Создаем уроки
        lesson = Lesson.objects.create(
            name="Первые шаги в Python",
            description="Знакомство с синтаксисом Python",
            video_url="https://youtube.com/python-intro",
            course=course,
            owner=test_user,
        )

        # Создаем платежи
        Payment.objects.create(
            user=test_user,
            course=course,
            amount=Decimal("15000.00"),
            payment_method="transfer",
            payment_date=datetime.datetime.now(),
        )

        Payment.objects.create(
            user=test_user,
            lesson=lesson,
            amount=Decimal("2500.00"),
            payment_method="cash",
            payment_date=datetime.datetime.now(),
        )

        self.stdout.write(self.style.SUCCESS("Successfully created test data"))
