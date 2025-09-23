from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from materials.models import Lesson, Course, Subscription
from users.models import User


class LessonsCreateTestCase(APITestCase):

    def setUp(self):
        """Подготовка данных"""
        self.user = User.objects.create_user(
            email="kaka@gmail.com",  # Убрал username, оставил только email
            password="kakas123",
        )
        self.course = Course.objects.create(
            name="Программирование",
            description="Описание курса",
            owner=self.user
        )
        self.lesson = Lesson.objects.create(
            course=self.course,
            video_url="https://www.youtube.com/",
            name="Основы Django",
            description="Описание урока",
            owner=self.user,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_lesson(self):
        """Тестирование создания урока"""
        url = reverse("materials:lesson-list-create")  # Возможно нужно изменить на materials вместо course
        data = {
            "name": "Основы Python",
            "description": "Описание урока",
            "course": self.course.id,
            "video_url": "https://www.youtube.com/",
        }
        response = self.client.post(url, data)

        # проверка статус кода
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # проверка содержимого критичных полей post-запроса
        response_data = response.json()
        self.assertEqual(response_data["name"], "Основы Python")
        self.assertEqual(response_data["course"], self.course.id)

        # проверка записи в БД
        self.assertTrue(Lesson.objects.filter(name="Основы Python").exists())

    def test_retrieve_lesson(self):
        """Тестирование просмотра отдельного урока"""
        url = reverse("materials:lesson-detail", args=(self.lesson.pk,))  # materials вместо course
        response = self.client.get(url)

        # проверка статус кода
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # проверка содержимого json
        response_data = response.json()
        self.assertEqual(response_data["name"], self.lesson.name)

    def test_update_lesson(self):
        """Тестирование редактирования урока"""
        url = reverse("materials:lessons_update", args=(self.lesson.pk,))  # materials вместо course
        update_data = {"name": "Основы ООП"}

        # отправляем обновлённые данные
        response = self.client.patch(url, update_data)
        data = response.json()

        # проверка статус кода
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # проверка содержимого json
        self.assertEqual(data.get("name"), "Основы ООП")

    def test_delete_lesson(self):
        """Тестирование удаления урока"""
        url = reverse("materials:lessons_destroy", args=(self.lesson.pk,))  # materials вместо course
        response = self.client.delete(url)

        # проверка статус кода
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # проверка количества уроков после удаления
        self.assertEqual(Lesson.objects.count(), 0)

    def test_list_lessons(self):
        """Тестирование просмотра списка уроков"""
        url = reverse("materials:lessons_list")  # materials вместо course
        response = self.client.get(url)

        # проверка статус кода
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_activate_subscription(self):
        """Тестирование работы подписки"""
        # Шаг 1. Авторизуем пользователя (уже сделано в setUp)
        # Шаг 2. Создадим новый курс
        course = Course.objects.create(
            name="Новый курс",
            description="Содержание курса",
            owner=self.user
        )

        # Отправляем запрос на URL подписки
        url = reverse("materials:subscription")
        data = {'course_id': self.course.id}  # Передаем ID курса
        response = self.client.post(url, data)  # Используем POST

        # Проверяем статус код и наличие ключа subscription_activate
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем, что подписка была создана
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())
