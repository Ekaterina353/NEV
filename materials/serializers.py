from rest_framework import serializers

from .models import Course, Lesson, Subscription
from .validators import VideoURLValidator, validate_video_url


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            "id",
            "name",
            "description",
            "preview",
            "video_url",
            "course",
            "owner",
        ]
        read_only_fields = ["owner"]
        validators = [VideoURLValidator(field="video_url")]


class CourseSerializer(serializers.ModelSerializer):
    lesson_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)  # Связанные уроки

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "description",
            "lesson_count",
            "is_subscribed",
            "lessons",
        ]

    def get_lesson_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.subscriptions.filter(user=request.user).exists()
        return False


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ["id", "user", "course", "created_at"]
        read_only_fields = ["user", "created_at"]
