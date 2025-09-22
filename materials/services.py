import stripe
from config.settings import STRIPE_API_KEY

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


def create_stripe_payment_intent(amount):
    """
    Создает Payment Intent в Stripe.

    Args:
        amount (int): Сумма платежа в наименьших единицах валюты (например, центы для USD).

    Returns:
        stripe.PaymentIntent: Объект PaymentIntent, созданный в Stripe.

    Raises:
        stripe.error.StripeError: В случае ошибки при создании PaymentIntent в Stripe.
    """
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='rub',  # Или другая валюта
            automatic_payment_methods={
                'enabled': True,
            },
        )
        return intent
    except stripe.error.StripeError as e:
        raise e
