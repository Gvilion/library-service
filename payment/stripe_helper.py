import stripe

from django.urls import reverse

from library_service import settings
from payment.models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY

FINE_MULTIPLIER = 2


def count_total_price(borrowing):

    if borrowing.borrow_date == borrowing.actual_return_date:
        days_borrowing = 1

    elif borrowing.expected_return_date >= borrowing.actual_return_date:
        days_borrowing = (borrowing.actual_return_date
                          - borrowing.borrow_date
                          ).days
    else:
        days_borrowing = (borrowing.expected_return_date
                          - borrowing.borrow_date
                          ).days

    price_in_cents = int(days_borrowing
                         * borrowing.book.daily_fee
                         * 100
                         )

    overdue_days = (borrowing.actual_return_date
                    - borrowing.expected_return_date
                    ).days

    fine_in_cents = int(overdue_days
                        * borrowing.book.daily_fee
                        * FINE_MULTIPLIER
                        * 100
                        ) if overdue_days > 0 else 0

    return price_in_cents + fine_in_cents


def create_payment(borrowing, session):
    payment = Payment.objects.create(
        status="PENDING",
        payment_type="PAYMENT",
        borrowing=borrowing,
        session_id=session.id,
        session_url=session.url,
        user=borrowing.user
    )

    if borrowing.actual_return_date > borrowing.expected_return_date:
        payment.payment_type = "FINE"

    payment.money_to_pay = round(
        count_total_price(borrowing) / 100, 2
    )
    payment.save()

    return payment


def create_stripe_session(borrowing, request):

    success_url = request.build_absolute_uri(
        reverse(
            "payment:payment-success",
            args=[borrowing.id]
        )
    )
    cancel_url = request.build_absolute_uri(
        reverse(
            "payment:payment-cancel",
            args=[borrowing.id]
        )
    )

    total_price_in_cents = count_total_price(borrowing)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "unit_amount": total_price_in_cents,
                "product_data": {
                    "name": borrowing.book.title,
                    "description": f"User: {borrowing.user.email}",
                },
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )

    payment = create_payment(borrowing, session)

    borrowing.payments.add(payment)
    borrowing.save()

    return session.url
