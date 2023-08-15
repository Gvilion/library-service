import stripe
from django.utils import timezone

from library_service import settings
from payment.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_session(borrowing):
    days_remaining = (borrowing.expected_return_date
                      - timezone.now().date()
                      ).days
    total_price_in_cents = int(days_remaining
                               * borrowing.book.daily_fee
                               * 100
                               )

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": 'usd',
                "unit_amount": total_price_in_cents,
                "product_data": {
                    "name":  borrowing.book.title,
                    "description": f"User: {borrowing.user.email}",
                },
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url="http://localhost:4242/success",  # temporary url
        cancel_url="http://localhost:4242/cancel",  # temporary url
    )

    payment = Payment.objects.create(
        status="PENDING",
        type="PAYMENT",
        borrowing=borrowing,
        session_id=session.id,
        session_url=session.url,
        user=borrowing.user
    )
    borrowing.payments.add(payment)

    return session.url
