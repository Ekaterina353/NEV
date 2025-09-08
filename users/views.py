from rest_framework.generics import UpdateAPIView
from .models import User, Payment
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import PaymentSerializer, UserSerializer
from rest_framework import filters, generics


class UserProfileUpdateView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class PaymentListView(generics.ListCreateAPIView):
        queryset = Payment.objects.all()
        serializer_class = PaymentSerializer
        filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
        filterset_fields = ["course", "lesson", "method"]
        ordering_fields = ["payment_date"]
        ordering = ["-payment_date"]  # По умолчанию — свежие сверху

