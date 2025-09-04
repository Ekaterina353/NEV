from rest_framework import serializers
from .models import Course, Lesson

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "name", "description"]


def get_lesson_count(obj):
    return obj.lessons.count()


class CourseSerializer(serializers.ModelSerializer):
    lesson_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)  # Связанные уроки

    class Meta:
        model = Course
        fields = ["id", "name", "description", "lesson_count", "lessons"]
