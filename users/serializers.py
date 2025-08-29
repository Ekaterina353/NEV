import os

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Payment

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "password", "phone", "city", "avatar"]
        read_only_fields = ["id"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    course_title = serializers.SerializerMethodField()
    lesson_title = serializers.SerializerMethodField()
    payment_method_display = serializers.SerializerMethodField()
    payment_status_display = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            "id",
            "payment_date",
            "amount",
            "payment_method",
            "payment_method_display",
            "payment_status",
            "payment_status_display",
            "course",
            "course_title",
            "lesson",
            "lesson_title",
            "stripe_session_id",
        ]
        extra_kwargs = {
            "course": {"write_only": True},
            "lesson": {"write_only": True},
            "stripe_session_id": {"read_only": True},
        }

    def get_course_title(self, obj):
        return obj.course.name if obj.course else None

    def get_lesson_title(self, obj):
        return obj.lesson.name if obj.lesson else None

    def get_payment_method_display(self, obj):
        return obj.get_payment_method_display()

    def get_payment_status_display(self, obj):
        return obj.get_payment_status_display()


class PublicProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "city", "avatar")
        read_only_fields = fields


class PrivateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "phone", "city", "avatar")
        extra_kwargs = {"email": {"read_only": True}}

    def validate_avatar(self, value):
        if value:
            ext = os.path.splitext(value.name)[1]
            valid_extensions = [".jpg", ".jpeg", ".png", ".gif"]
            if not ext.lower() in valid_extensions:
                raise ValidationError("Неподдерживаемый формат изображения")
            if value.size > 2 * 1024 * 1024:
                raise ValidationError("Файл слишком большой (макс. 2MB)")
        return value


class UserProfileWithPaymentsSerializer(serializers.ModelSerializer):
    payments = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar",
            "payments",
        )
        extra_kwargs = {
            "email": {"read_only": True},
            "last_name": {"write_only": True},
        }

    def get_payments(self, obj):
        payments = obj.payments.all().order_by("-payment_date")[:5]
        return PaymentSerializer(payments, many=True).data
