from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (OpenApiExample, OpenApiParameter,
                                   extend_schema, extend_schema_view)
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course, Lesson, Subscription
from .paginators import CoursePagination, LessonPagination
from .permissions import IsOwnerOrModerator
from .serializers import (CourseSerializer, LessonSerializer,
                          SubscriptionSerializer)
from .tasks import send_course_update_email


@extend_schema_view(
    list=extend_schema(
        summary="Список курсов",
        description="Получить список всех курсов пользователя",
        tags=["Курсы"],
    ),
    create=extend_schema(
        summary="Создать курс", description="Создать новый курс", tags=["Курсы"]
    ),
    retrieve=extend_schema(
        summary="Получить курс",
        description="Получить детальную информацию о курсе",
        tags=["Курсы"],
    ),
    update=extend_schema(
        summary="Обновить курс", description="Полностью обновить курс", tags=["Курсы"]
    ),
    partial_update=extend_schema(
        summary="Частично обновить курс",
        description="Частично обновить курс",
        tags=["Курсы"],
    ),
    destroy=extend_schema(
        summary="Удалить курс", description="Удалить курс", tags=["Курсы"]
    ),
)
class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    queryset = Course.objects.none()
    pagination_class = CoursePagination

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [IsAuthenticated]
        elif self.action in ["update", "partial_update", "retrieve"]:
            self.permission_classes = [IsOwnerOrModerator]
        elif self.action == "destroy":
            self.permission_classes = [IsOwnerOrModerator]
        return super().get_permissions()

    def get_queryset(self):
        return Course.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        last_updated = instance.updated_at
        response = super().update(request, *args, **kwargs)
        instance.refresh_from_db()
        if timezone.now() - last_updated > timedelta(hours=4):
            material_title = getattr(instance, "name", "материал")
            for sub in instance.subscriptions.all():
                send_course_update_email.delay(
                    sub.user.email, instance.name, material_title
                )
        return response

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        last_updated = instance.updated_at
        response = super().partial_update(request, *args, **kwargs)
        instance.refresh_from_db()
        if timezone.now() - last_updated > timedelta(hours=4):
            material_title = getattr(instance, "name", "материал")
            for sub in instance.subscriptions.all():
                send_course_update_email.delay(
                    sub.user.email, instance.name, material_title
                )
        return response


@extend_schema_view(
    get=extend_schema(
        summary="Список уроков",
        description="Получить список всех уроков пользователя",
        tags=["Уроки"],
    ),
    post=extend_schema(
        summary="Создать урок", description="Создать новый урок", tags=["Уроки"]
    ),
)
class LessonListCreateView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    queryset = Lesson.objects.none()
    pagination_class = LessonPagination

    def get_queryset(self):
        return Lesson.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


@extend_schema(
    summary="Управление подпиской",
    description="Добавить или удалить подписку на курс. Если подписка существует - удаляет её (204), если нет - создает новую (201)",
    tags=["Подписки"],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "course_id": {"type": "integer", "description": "ID курса для подписки"}
            },
            "required": ["course_id"],
        }
    },
    responses={
        201: {"description": "Подписка создана", "type": "object", "properties": {}},
        204: {"description": "Подписка удалена", "type": "object", "properties": {}},
    },
    examples=[
        OpenApiExample(
            "Добавить подписку",
            value={"course_id": 1},
            description="Пример запроса для добавления подписки на курс с ID 1",
        )
    ],
)
class SubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course_id")
        course = get_object_or_404(Course, id=course_id)

        subscription = Subscription.objects.filter(user=user, course=course)

        if subscription.exists():
            subscription.delete()
            return Response(status=204)  # No Content - подписка удалена
        else:
            Subscription.objects.create(user=user, course=course)
            return Response(status=201)  # Created - подписка создана


@extend_schema_view(
    get=extend_schema(
        summary="Получить урок",
        description="Получить детальную информацию об уроке",
        tags=["Уроки"],
    ),
    put=extend_schema(
        summary="Обновить урок", description="Полностью обновить урок", tags=["Уроки"]
    ),
    patch=extend_schema(
        summary="Частично обновить урок",
        description="Частично обновить урок",
        tags=["Уроки"],
    ),
    delete=extend_schema(
        summary="Удалить урок", description="Удалить урок", tags=["Уроки"]
    ),
)
class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]
    queryset = Lesson.objects.none()

    def get_queryset(self):
        return Lesson.objects.filter(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        course = instance.course
        last_updated = course.updated_at
        response = super().update(request, *args, **kwargs)
        course.refresh_from_db()
        if timezone.now() - last_updated > timedelta(hours=4):
            material_title = getattr(instance, "name", "материал")
            for sub in course.subscriptions.all():
                send_course_update_email.delay(
                    sub.user.email, course.name, material_title
                )
        return response

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        course = instance.course
        last_updated = course.updated_at
        response = super().partial_update(request, *args, **kwargs)
        course.refresh_from_db()
        if timezone.now() - last_updated > timedelta(hours=4):
            material_title = getattr(instance, "name", "материал")
            for sub in course.subscriptions.all():
                send_course_update_email.delay(
                    sub.user.email, course.name, material_title
                )
        return response
