from django.urls import reverse
from rest_framework.test import APITestCase

from materials.models import Course, Lesson, Subscription
from users.models import User


class TestCase(APITestCase):
    """
    Базовый тестовый класс для всех тестов
    """

    def setUp(self):
        self.user = User.objects.create(email="test@test.ru")
        self.course = Course.objects.create(name="Test Course", owner=self.user)
        self.lesson = Lesson.objects.create(
            name="Test Lesson", course=self.course, owner=self.user
        )
        self.client.force_authenticate(user=self.user)


class CourseTestCase(TestCase, APITestCase):
    """
    Тесты для работы с курсами
    """

    def test_course_retrieve(self):
        """
        Тест получения курса по ID
        """
        url = reverse("materials:course-detail", args=(self.course.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], self.course.name)

    def test_course_create(self):
        """
        Тест создания нового курса
        """
        url = reverse("materials:course-list")
        data = {
            "name": "Test Course 2",
            "description": "Test description",
            "owner": self.user.pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Course.objects.count(), 2)

    def test_course_update(self):
        """
        Тест изменения курса по ID
        """
        url = reverse("materials:course-detail", args=(self.course.pk,))
        data = {
            "name": "Updated Test Course",
            "description": "Updated test description",
        }
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Course.objects.get(pk=self.course.pk).name, "Updated Test Course"
        )

    def test_course_delete(self):
        """
        Тест удаления курса по ID
        """
        url = reverse("materials:course-detail", args=(self.course.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Course.objects.count(), 0)


class LessonTestCase(TestCase, APITestCase):
    """
    Тесты для работы с уроками
    """

    def test_lesson_retrieve(self):
        """
        Тест получения урока по ID
        """
        url = reverse("materials:lessons-retrieve", args=(self.lesson.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], self.lesson.name)

    def test_lesson_create(self):
        """
        Тест создания нового урока
        """
        url = reverse("materials:lessons-create")
        data = {
            "name": "Test Lesson 2",
            "course": self.course.pk,
            "owner": self.user.pk,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_lesson_update(self):
        """
        Тест изменения урока по ID
        """
        url = reverse("materials:lessons-update", args=(self.lesson.pk,))
        data = {
            "name": "Updated Test Lesson",
            "course": self.course.pk,
            "owner": self.user.pk,
        }
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Lesson.objects.get(pk=self.lesson.pk).name, "Updated Test Lesson"
        )

    def test_lesson_delete(self):
        """
        Тест удаления урока по ID
        """
        url = reverse("materials:lessons-destroy", args=(self.lesson.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Lesson.objects.count(), 0)


class SubscriptionTest(TestCase, APITestCase):
    """
    Тесты для работы с подписками
    """

    def test_subscription(self):
        """
        Тест подписки на курс
        """
        url = reverse("materials:subscription")
        data = {
            "user_id": self.user.pk,
            "course_id": self.course.pk,
        }

        # Проверка оформления подписки
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Подписка добавлена")
