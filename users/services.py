import stripe
from django.conf import settings
from django.core.exceptions import ValidationError

# Настройка Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Сервис для работы с Stripe API"""

    @staticmethod
    def create_product(name, description=None):
        """
        Создать продукт в Stripe

        Args:
            name (str): Название продукта
            description (str, optional): Описание продукта

        Returns:
            dict: Данные созданного продукта
        """
        try:
            product_data = {"name": name, "description": description or f"Курс: {name}"}

            product = stripe.Product.create(**product_data)
            return {
                "id": product.id,
                "name": product.name,
                "description": product.description,
            }
        except stripe.error.StripeError as e:
            raise ValidationError(f"Ошибка создания продукта в Stripe: {str(e)}")

    @staticmethod
    def create_price(product_id, amount, currency="rub"):
        """
        Создать цену для продукта в Stripe

        Args:
            product_id (str): ID продукта в Stripe
            amount (Decimal): Сумма в рублях
            currency (str): Валюта (по умолчанию 'rub')

        Returns:
            dict: Данные созданной цены
        """
        try:
            # Stripe требует сумму в копейках (умножаем на 100)
            amount_cents = int(float(amount) * 100)

            price_data = {
                "product": product_id,
                "unit_amount": amount_cents,
                "currency": currency,
                "recurring": None,  # Разовый платеж
            }

            price = stripe.Price.create(**price_data)
            return {
                "id": price.id,
                "product_id": price.product,
                "amount": price.unit_amount,
                "currency": price.currency,
            }
        except stripe.error.StripeError as e:
            raise ValidationError(f"Ошибка создания цены в Stripe: {str(e)}")

    @staticmethod
    def create_checkout_session(price_id, success_url, cancel_url, metadata=None):
        """
        Создать сессию для оплаты

        Args:
            price_id (str): ID цены в Stripe
            success_url (str): URL для перенаправления после успешной оплаты
            cancel_url (str): URL для перенаправления при отмене
            metadata (dict, optional): Дополнительные метаданные

        Returns:
            dict: Данные сессии оплаты
        """
        try:
            session_data = {
                "payment_method_types": ["card"],
                "line_items": [
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                "mode": "payment",
                "success_url": success_url,
                "cancel_url": cancel_url,
            }

            if metadata:
                session_data["metadata"] = metadata

            session = stripe.checkout.Session.create(**session_data)
            return {
                "id": session.id,
                "url": session.url,
                "payment_status": session.payment_status,
                "amount_total": session.amount_total,
                "currency": session.currency,
            }
        except stripe.error.StripeError as e:
            raise ValidationError(f"Ошибка создания сессии оплаты: {str(e)}")

    @staticmethod
    def get_session_status(session_id):
        """
        Получить статус сессии оплаты

        Args:
            session_id (str): ID сессии в Stripe

        Returns:
            dict: Статус сессии
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return {
                "id": session.id,
                "payment_status": session.payment_status,
                "status": session.status,
                "amount_total": session.amount_total,
                "currency": session.currency,
                "customer_email": (
                    session.customer_details.get("email")
                    if session.customer_details
                    else None
                ),
            }
        except stripe.error.StripeError as e:
            raise ValidationError(f"Ошибка получения статуса сессии: {str(e)}")
