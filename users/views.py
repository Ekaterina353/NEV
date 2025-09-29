import stripe
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from config import settings
from . import serializers
from .filters import PaymentFilter
from .models import Payment
from .permissions import IsProfileOwner
from .serializers import (
    PaymentSerializer,
    PrivateProfileSerializer,
    PublicProfileSerializer,
    UserProfileWithPaymentsSerializer,
    UserSerializer,
)

User = get_user_model()
stripe.api_key = settings.STRIPE_API_KEY

class PaymentListView(generics.ListCreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

        def perform_create(self, serializer):
            """
            Создает платеж через Stripe используя Stripe Product, Price и Session.
            """
            payment = serializer.save(user=self.request.user)  # Сохраняем пользователя
            product_id = create_stripe_product(payment.course)
            price = create_stripe_price(product_id, payment.amount)
            session = create_stripe_session(price["id"])
            payment.payment_id = session.id  # Сохраняем id сессии
            payment.save()

    def create_stripe_product(content_object):
        """
        Создает продукт в Stripe.
        """
        try:
            product = stripe.Product.create(
                name=content_object.name,  # Изменено title на name
            )
            return product.id
        except stripe.error.StripeError as e:
            print(f'Ошибка создания продукта: {e}')
            return None

    def create_stripe_price(product_id, price):
        try:
            stripe_price = stripe.Price.create(
                currency='rub',
                unit_amount=int(price * 100),
                product=product_id,
            )
            return stripe_price
        except stripe.error.StripeError as e:
            print(f'Ошибка создания цены: {e}')
            return None

    def create_stripe_session(price_id):
        """
        Создает платежную сессию в Stripe.
        """
        try:
            stripe_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='payment',
                success_url='https://example.com/success',  # Замените на реальный URL
                cancel_url='https://example.com/cancel',  # Замените на реальный URL
            )
            return stripe_session
        except stripe.error.StripeError as e:
            print(f'Ошибка создания сессии: {e}')
            return None


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return super().get_permissions()


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__' #Добавил все поля
        #fields = ["user", "payment_method"] #Добавил нужные поля


class UserProfileDetailView(generics.RetrieveAPIView):
    queryset = User.objects.only("id", "email", "first_name", "city", "avatar")
    serializer_class = PublicProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsProfileOwner]
    lookup_field = "pk"


class OwnProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileWithPaymentsSerializer
    permission_classes = [permissions.IsAuthenticated, IsProfileOwner]

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return User.objects.prefetch_related("payments", "payments__course", "payments__lesson").filter(
            pk=self.request.user.pk
        )


class PaymentHistoryView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)


class PaymentStatsView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        total = Payment.objects.filter(user=request.user).aggregate(total_amount=Sum("amount"))["total_amount"] or 0

        by_method = (
            Payment.objects.filter(user=request.user)
            .values("payment_method")
            .annotate(total=Sum("amount"), count=Count("id"))
        )

        return Response({"total_amount": total, "by_method": by_method})
