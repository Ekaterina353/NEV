from django.db import models
from django.conf import \
    settings  # Используем settings для ссылки на модель пользователя

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

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

class Lesson(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(verbose_name = "Описание")
    preview = models.ImageField(
    upload_to = "lesson_previews/", null = True, blank = True, verbose_name = "Превью"
    )
    ideo_url = models.URLField(verbose_name="Ссылка на видео")
    course = models.ForeignKey(
        Course, on_delete = models.CASCADE, related_name = "lessons", verbose_name = "Курс"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
        related_name = "lessons",
        verbose_name = "Владелец",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"