from django.urls import include, path
from rest_framework.routers import DefaultRouter
from materials.views import CourseViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    # Добавляем namespace для приложения materials
    path('api/', include(('materials.urls', 'materials'), namespace='materials')),
    # Добавляем namespace для приложения users
    path('api/users/', include(('users.urls', 'users'), namespace='users')),
    path("api/", include("users.urls")),
]
