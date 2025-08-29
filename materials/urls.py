from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (CourseViewSet, LessonDetailView, LessonListCreateView,
                    SubscriptionView)

router = DefaultRouter()
router.register(r"courses", CourseViewSet)


urlpatterns = [
    path("lessons/", LessonListCreateView.as_view(), name="lesson-list-create"),
    path("lessons/<int:pk>/", LessonDetailView.as_view(), name="lesson-detail"),
    path("subscriptions/", SubscriptionView.as_view(), name="subscription"),
] + router.urls
