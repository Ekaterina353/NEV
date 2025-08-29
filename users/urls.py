from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from .views import (OwnProfileUpdateView, PaymentCancelView,
                    PaymentHistoryView, PaymentListView, PaymentStatsView,
                    PaymentSuccessView, StripePaymentCreateView,
                    StripePaymentStatusView, UserProfileDetailView,
                    UserViewSet)

router = DefaultRouter()
router.register(r"users", UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("payments/", PaymentListView.as_view(), name="payment-list"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "users/<int:pk>/", UserProfileDetailView.as_view(), name="user-profile-detail"
    ),
    path("users/me/", OwnProfileUpdateView.as_view(), name="own-profile"),
    path("users/me/payments/", PaymentHistoryView.as_view(), name="user-payments"),
    path("users/me/payments/stats/", PaymentStatsView.as_view(), name="payment-stats"),
    # Stripe payment endpoints
    path(
        "payments/stripe/create/",
        StripePaymentCreateView.as_view(),
        name="stripe-payment-create",
    ),
    path(
        "payments/stripe/status/",
        StripePaymentStatusView.as_view(),
        name="stripe-payment-status",
    ),
    path("payments/success/", PaymentSuccessView.as_view(), name="payment-success"),
    path("payments/cancel/", PaymentCancelView.as_view(), name="payment-cancel"),
]
