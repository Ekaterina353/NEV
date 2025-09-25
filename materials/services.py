import stripe
from config.settings import STRIPE_API_KEY
from rest_framework import generics
from rest_framework import serializers


stripe.api_key = STRIPE_API_KEY


def create_stripe_product(content_object):
    try:
        product = stripe.Product.create(
            name=content_object.title,
            type='service'
        )
        content_object.stripe_product_id = product.id
        content_object.save()
        return product.id
    except stripe.error.StripeError as e:
        print(f'Ошибка создания продукта: {e}')
        return None


def create_stripe_price(content):
    try:
        stripe_price = stripe.Price.create(
            currency='rub',
            unit_amount=content.price * 100,
            product=content.stripe_product_id,
        )
        return stripe_price
    except stripe.error.StripeError as e:
        print(f'Ошибка создания цены: {e}')
        return None


def create_stripe_session(stripe_price_id):
    session = stripe.checkout.Session.create(
        success_url="http://127.0.0.1:8000/",
        payment_method_types=['card'],
        line_items=[{
            "price": stripe_price_id,
            "quantity": 1,
        }],
        mode="payment"
    )
    return session.id, session.url

class PaymentListView(generics.CreateAPIView):
    serializer_class = serializers.Serializer  # Укажите актуальный сериализатор

    def perform_create(self, serializer):
        # Сохраняем платеж
        payment = serializer.save()

        # Предполагаем, что в payment есть поле content, которое содержит Product/Course
        content = payment.content

        # Создание stripe product
        stripe_product_id = create_stripe_product(content)

        if not stripe_product_id:
            raise serializers.ValidationError("Ошибка при создании Stripe Product")

        # Создание stripe price
        stripe_price = create_stripe_price(content)

        if not stripe_price:
            raise serializers.ValidationError("Ошибка при создании Stripe Price")


        payment.stripe_price_id = stripe_price.id
        payment.save()

        # Создание stripe session
        session_id, session_url = create_stripe_session(stripe_price.id)

        # Обновляем модель Payment с session_id и session_url
        payment.session_id = session_id
        payment.session_url = session_url
        payment.save()