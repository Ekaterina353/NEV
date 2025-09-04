from django.urls import path
from .views import UserProfileUpdateView

urlpatterns = [
    path('profile/update/<int:pk>/', UserProfileUpdateView.as_view(), name='user-update'),
]
