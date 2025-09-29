import stripe
from config.settings import STRIPE_API_KEY



stripe.api_key = STRIPE_API_KEY


def create_stripe_product(content_object):
    try:
        product = stripe.Product.create(
            name=content_object.name,
            type='service'
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
