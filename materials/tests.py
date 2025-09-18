from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson
from users.models import User, Follow


class CourseTestCase(APITestCase):
    def setUp(self):
        # Создание пользователя, курса, урока и подписки для тестов
        self.user = User.objects.create(email="test@test.com")
        self.course = Course.objects.create(
            title="test_course", description="test_description", owner=self.user
        )
        self.lesson = Lesson.objects.create(
            title="test_lesson", courses=self.course, owner=self.user
        )
        self.follow = Follow.objects.create(courses=self.course, user=self.user)
        # Аутентификация пользователя для выполнения запросов
        self.client.force_authenticate(user=self.user)

    def test_course_retrieve(self):
        # Получение информации о курсе
        url = reverse("materials:course-detail", args=(self.course.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("title"), self.course.title)

    def test_course_create(self):
        # Создание курса
        url = reverse("materials:course-list")
        data = {"title": "Курс1", "link": "https://www.youtube.com/s"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.all().count(), 2)

    def test_course_update(self):
        # Обновление курса
        url = reverse("materials:course-detail", args=(self.course.pk,))
        data = {"title": "Курс", "link": "https://www.youtube.com/"}
        response = self.client.patch(url, data)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("title"), "Курс")

    def test_course_delete(self):
        # Удаление курса
        url = reverse("materials:course-detail", args=(self.course.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Course.objects.all().count(), 0)

    def test_course_list(self):
        # Получение списка курсов
        url = reverse("materials:course-list")
        response = self.client.get(url)
        data = response.json()
        result = data["results"]
        res = len(result[0])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(res, 6)

    def test_follow(self):
        # Проверка подписки на курс
        url = reverse("users:follow-check", args=(self.course.pk,))
        data = {"id": self.course.pk}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("message"), "подписка удалена")


class LessonsTestCase(APITestCase):
    def setUp(self):
        # Создание пользователя, курса и урока для тестов
        self.user = User.objects.create(email="test@test.com")
        self.course = Course.objects.create(
            title="test_course", description="test_description", owner=self.user
        )
        self.lesson = Lesson.objects.create(
            title="test_lesson", courses=self.course, owner=self.user
        )
        # Аутентификация пользователя для выполнения запросов
        self.client.force_authenticate(user=self.user)

    def test_lesson_retrieve(self):
        # Получение информации об уроке
        url = reverse("materials:lessons-retrieve", args=(self.lesson.pk,))
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("title"), self.lesson.title)

    def test_lesson_create(self):
        # Создание урока
        url = reverse("materials:lessons-create")
        data = {"title": "Урок"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.all().count(), 2)

    def test_lesson_update(self):
        # Обновление урока
        url = reverse("materials:lessons-update", args=(self.lesson.pk,))
        data = {"title": "Урок3"}
        response = self.client.patch(url, data)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("title"), "Урок3")

    def test_lesson_delete(self):
        # Удаление урока
        url = reverse("materials:lessons-delete", args=(self.lesson.pk,))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.all().count(), 0)

    def test_lesson_list(self):
        # Получение списка уроков
        url = reverse("materials:lessons-list")
        response = self.client.get(url)
        data = response.json()
        result = data["results"]
        res = len(result[0])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
