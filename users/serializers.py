from rest_framework import serializers
from .models import User, Payment
from materials.serializers import CourseSerializer, LessonSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'phone', 'city', 'avatar']


class PaymentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    lesson = LessonSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ["id", "payment_date", "course", "lesson", "amount", "method"]
