import django_filters
from django.db.models import Q

from .models import Payment


class PaymentFilter(django_filters.FilterSet):
    course = django_filters.NumberFilter(field_name="course__id")
    lesson = django_filters.NumberFilter(field_name="lesson__id")
    payment_method = django_filters.CharFilter(
        field_name="payment_method", lookup_expr="iexact"
    )
    search = django_filters.CharFilter(method="custom_search")

    def custom_search(self, queryset, name, value):
        return queryset.filter(
            Q(course__name__icontains=value) | Q(lesson__name__icontains=value)
        )

    class Meta:
        model = Payment
        fields = ["course", "lesson", "payment_method"]
