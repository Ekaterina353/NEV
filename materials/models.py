from django.conf import \
    settings  # Используем settings для ссылки на модель пользователя
from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    preview = models.ImageField(
        upload_to="course_previews/", null=True, blank=True, verbose_name="Превью"
    )
    description = models.TextField(verbose_name="Описание")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name="Владелец",
        default=1,
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Время обновления")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ["name"]


class Lesson(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    preview = models.ImageField(
        upload_to="lesson_previews/", null=True, blank=True, verbose_name="Превью"
    )
    video_url = models.URLField(verbose_name="Ссылка на видео")
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lessons", verbose_name="Курс"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Владелец",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["name"]


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Пользователь",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Курс",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подписки")

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = [
            "user",
            "course",
        ]  # Один пользователь может подписаться на курс только один раз

    def __str__(self):
        return f"{self.user.email} - {self.course.name}"
