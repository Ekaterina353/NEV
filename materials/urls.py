from django.urls import path
from rest_framework.routers import DefaultRouter

from materials.apps import MaterialsConfig

from .views import (
    CourseViewSet,
    LessonAPIDestroy,
    LessonAPIUpdate,
    LessonAPIView,
    LessonDetailView,
    LessonListCreateView,
    SubscriptionView,
)

app_name = MaterialsConfig.name
router = DefaultRouter()
router.register(r"courses", CourseViewSet)

urlpatterns = [
    path("lessons/", LessonAPIView.as_view(), name="lessons_list"),
    path("lessons/create/", LessonListCreateView.as_view(), name="lesson-list-create"),
    path("lessons/update/<int:pk>", LessonAPIUpdate.as_view(), name="lessons_update"),
    path("lessons/destroy/<int:pk>", LessonAPIDestroy.as_view(), name="lessons_destroy"),
    path("lessons/<int:pk>/", LessonDetailView.as_view(), name="lesson-detail"),
    path("subscriptions/", SubscriptionView.as_view(), name="subscription"),
] + router.urls
