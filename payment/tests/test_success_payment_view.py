import datetime
from datetime import timedelta

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from books.models import Book
from borrowings.models import Borrowing

from payment.models import Payment

from payment.tests.test_model import (
    CURRENT_DAY,
    BORROWING_DAYS
)


def success_url(borrowing_id):
    return reverse(
        "payment:payment-success",
        args=[borrowing_id]
    )


class SuccessPaymentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@user.com",
            "user123456",
        )

        self.client.force_authenticate(self.user)

        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=10,
            daily_fee=Decimal("12.99")
        )

        self.borrowing = Borrowing.objects.create(
            expected_return_date=CURRENT_DAY + timedelta(
                days=BORROWING_DAYS
            ),
            book=self.book,
            user=self.user,
        )

        self.money_to_pay = round(
            self.book.daily_fee * BORROWING_DAYS, 2
        )

        self.payment = Payment.objects.create(
            status="PENDING",
            payment_type="PAYMENT",
            borrowing=self.borrowing,
            session_url="https://checkout.stripe.com/c/pay/cs_test",
            session_id="cs_test",
            money_to_pay=self.money_to_pay,
            user=self.user,
        )

    def test_get_success_payment(self):
        url = success_url(self.borrowing.id)
        request = self.client.get(url)

        expected_status = "PAID"
        expected_actual_return_date = datetime.date.today()

        self.borrowing.refresh_from_db()
        self.payment.refresh_from_db()

        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(self.payment.status, expected_status)
        self.assertEqual(self.borrowing.actual_return_date, expected_actual_return_date)
