from django.urls import path
from .views import UserProfileUpdateView, PaymentListView

urlpatterns = [
    path('profile/update/<int:pk>/', UserProfileUpdateView.as_view(), name='user-update'),
path("payments/", PaymentListView.as_view(), name="payment-list"),
]
