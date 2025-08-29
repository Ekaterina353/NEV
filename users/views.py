from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (OpenApiExample, OpenApiParameter,
                                   extend_schema, extend_schema_view)
from rest_framework import generics, permissions, status, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import PaymentFilter
from .models import Payment
from .permissions import IsProfileOwner
from .serializers import (PaymentSerializer, PrivateProfileSerializer,
                          PublicProfileSerializer,
                          UserProfileWithPaymentsSerializer, UserSerializer)
from .services import StripeService

User = get_user_model()


@extend_schema_view(
    get=extend_schema(
        summary="Список платежей",
        description="Получить список всех платежей пользователя с возможностью фильтрации и сортировки",
        tags=["Платежи"],
        parameters=[
            OpenApiParameter(
                name="course",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Фильтр по ID курса",
            ),
            OpenApiParameter(
                name="lesson",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Фильтр по ID урока",
            ),
            OpenApiParameter(
                name="payment_method",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Фильтр по способу оплаты (cash/transfer)",
            ),
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Сортировка (payment_date или -payment_date)",
            ),
        ],
    ),
    post=extend_schema(
        summary="Создать платеж", description="Создать новый платеж", tags=["Платежи"]
    ),
)
class PaymentListView(generics.ListCreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)


@extend_schema_view(
    list=extend_schema(
        summary="Список пользователей",
        description="Получить список всех пользователей",
        tags=["Пользователи"],
    ),
    create=extend_schema(
        summary="Регистрация пользователя",
        description="Создать нового пользователя (регистрация)",
        tags=["Пользователи"],
    ),
    retrieve=extend_schema(
        summary="Получить пользователя",
        description="Получить информацию о пользователе",
        tags=["Пользователи"],
    ),
    update=extend_schema(
        summary="Обновить пользователя",
        description="Полностью обновить пользователя",
        tags=["Пользователи"],
    ),
    partial_update=extend_schema(
        summary="Частично обновить пользователя",
        description="Частично обновить пользователя",
        tags=["Пользователи"],
    ),
    destroy=extend_schema(
        summary="Удалить пользователя",
        description="Удалить пользователя",
        tags=["Пользователи"],
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return super().get_permissions()


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
        return User.objects.prefetch_related(
            "payments", "payments__course", "payments__lesson"
        ).filter(pk=self.request.user.pk)


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
        total = (
            Payment.objects.filter(user=request.user).aggregate(
                total_amount=Sum("amount")
            )["total_amount"]
            or 0
        )

        by_method = (
            Payment.objects.filter(user=request.user)
            .values("payment_method")
            .annotate(total=Sum("amount"), count=Count("id"))
        )

        return Response({"total_amount": total, "by_method": by_method})


@extend_schema(
    summary="Создать платеж через Stripe",
    description="Создать платеж для курса или урока через Stripe и получить ссылку на оплату",
    tags=["Stripe Платежи"],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "course_id": {"type": "integer", "description": "ID курса для оплаты"},
                "lesson_id": {"type": "integer", "description": "ID урока для оплаты"},
                "amount": {"type": "number", "description": "Сумма оплаты в рублях"},
            },
            "required": ["amount"],
        }
    },
    responses={
        201: {
            "description": "Платеж создан",
            "type": "object",
            "properties": {
                "payment_id": {"type": "integer"},
                "checkout_url": {"type": "string"},
                "session_id": {"type": "string"},
            },
        },
        400: {
            "description": "Ошибка валидации",
            "type": "object",
            "properties": {"error": {"type": "string"}},
        },
    },
    examples=[
        OpenApiExample(
            "Оплата курса",
            value={"course_id": 1, "amount": 5000.00},
            description="Пример запроса для оплаты курса с ID 1 на сумму 5000 рублей",
        ),
        OpenApiExample(
            "Оплата урока",
            value={"lesson_id": 1, "amount": 1000.00},
            description="Пример запроса для оплаты урока с ID 1 на сумму 1000 рублей",
        ),
    ],
)
class StripePaymentCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            course_id = request.data.get("course_id")
            lesson_id = request.data.get("lesson_id")
            amount = request.data.get("amount")

            if not amount:
                return Response(
                    {"error": "Сумма оплаты обязательна"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not course_id and not lesson_id:
                return Response(
                    {"error": "Необходимо указать course_id или lesson_id"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if course_id and lesson_id:
                return Response(
                    {"error": "Нельзя оплачивать курс и урок одновременно"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Получаем объект курса или урока
            if course_id:
                from materials.models import Course

                item = get_object_or_404(Course, id=course_id)
                item_type = "course"
            else:
                from materials.models import Lesson

                item = get_object_or_404(Lesson, id=lesson_id)
                item_type = "lesson"

            # Создаем платеж в нашей системе
            payment = Payment.objects.create(
                user=request.user,
                course=item if item_type == "course" else None,
                lesson=item if item_type == "lesson" else None,
                amount=amount,
                payment_method="stripe",
                payment_status="pending",
            )

            # Создаем продукт в Stripe
            product_data = StripeService.create_product(
                name=item.name, description=item.description
            )

            # Создаем цену в Stripe
            price_data = StripeService.create_price(
                product_id=product_data["id"], amount=amount
            )

            # Создаем сессию оплаты
            success_url = request.build_absolute_uri(reverse("payment-success"))
            cancel_url = request.build_absolute_uri(reverse("payment-cancel"))

            session_data = StripeService.create_checkout_session(
                price_id=price_data["id"],
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "payment_id": str(payment.id),
                    "user_id": str(request.user.id),
                    "item_type": item_type,
                    "item_id": str(item.id),
                },
            )

            # Обновляем платеж с данными Stripe
            payment.stripe_product_id = product_data["id"]
            payment.stripe_price_id = price_data["id"]
            payment.stripe_session_id = session_data["id"]
            payment.save()

            return Response(
                {
                    "payment_id": payment.id,
                    "checkout_url": session_data["url"],
                    "session_id": session_data["id"],
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Проверить статус платежа",
    description="Проверить статус платежа в Stripe по ID сессии",
    tags=["Stripe Платежи"],
    parameters=[
        OpenApiParameter(
            name="session_id",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="ID сессии в Stripe",
            required=True,
        )
    ],
    responses={
        200: {
            "description": "Статус платежа",
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
                "payment_status": {"type": "string"},
                "status": {"type": "string"},
                "amount_total": {"type": "integer"},
                "currency": {"type": "string"},
                "customer_email": {"type": "string"},
            },
        },
        400: {
            "description": "Ошибка",
            "type": "object",
            "properties": {"error": {"type": "string"}},
        },
    },
)
class StripePaymentStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        session_id = request.query_params.get("session_id")

        if not session_id:
            return Response(
                {"error": "session_id обязателен"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Получаем статус сессии из Stripe
            session_status = StripeService.get_session_status(session_id)

            # Обновляем статус платежа в нашей системе
            payment = Payment.objects.filter(
                stripe_session_id=session_id, user=request.user
            ).first()

            if payment:
                if session_status["payment_status"] == "paid":
                    payment.payment_status = "paid"
                elif session_status["payment_status"] == "unpaid":
                    payment.payment_status = "failed"
                payment.save()

            return Response(session_status)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Успешная оплата",
    description="Страница успешной оплаты (для перенаправления из Stripe)",
    tags=["Stripe Платежи"],
    responses={
        200: {
            "description": "Оплата прошла успешно",
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "payment_id": {"type": "integer"},
            },
        }
    },
)
class PaymentSuccessView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        session_id = request.query_params.get("session_id")

        if session_id:
            try:
                # Обновляем статус платежа
                payment = Payment.objects.filter(
                    stripe_session_id=session_id, user=request.user
                ).first()

                if payment:
                    payment.payment_status = "paid"
                    payment.save()

                    return Response(
                        {"message": "Оплата прошла успешно!", "payment_id": payment.id}
                    )
            except Exception:
                pass

        return Response({"message": "Оплата прошла успешно!"})


@extend_schema(
    summary="Отмена оплаты",
    description="Страница отмены оплаты (для перенаправления из Stripe)",
    tags=["Stripe Платежи"],
    responses={
        200: {
            "description": "Оплата отменена",
            "type": "object",
            "properties": {"message": {"type": "string"}},
        }
    },
)
class PaymentCancelView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        session_id = request.query_params.get("session_id")

        if session_id:
            try:
                # Обновляем статус платежа
                payment = Payment.objects.filter(
                    stripe_session_id=session_id, user=request.user
                ).first()

                if payment:
                    payment.payment_status = "cancelled"
                    payment.save()
            except Exception:
                pass

        return Response({"message": "Оплата была отменена"})
