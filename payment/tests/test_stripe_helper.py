from datetime import timedelta
from unittest.mock import Mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from books.models import Book
from borrowings.models import Borrowing
from payment.stripe_helper import count_total_price, create_payment
from payment.tests.test_model import CURRENT_DAY, BORROWING_DAYS


class StripeHelperTest(TestCase):
    def setUp(self):
        self.email = "test@post.com"
        self.password = "user123456"

        self.user = get_user_model().objects.create_user(
            email=self.email,
            password=self.password
        )

        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=10,
            daily_fee=12.99
        )

        self.borrowing = Borrowing.objects.create(
            expected_return_date=CURRENT_DAY + timedelta(
                days=BORROWING_DAYS
            ),
            book=self.book,
            user=self.user,
        )

    def test_count_total_price_payment(self):
        borrowing_days = 2
        self.borrowing.actual_return_date = CURRENT_DAY + timedelta(
            days=borrowing_days
        )

        self.borrowing.save()

        price_in_cents = count_total_price(self.borrowing)
        expected_price_in_cents = (self.borrowing.book.daily_fee
                                   * borrowing_days
                                   * 100)

        self.assertEqual(
            price_in_cents,
            expected_price_in_cents
        )

    def test_count_total_price_payment_fine(self):
        borrowing_days_total = 6

        self.borrowing.actual_return_date = CURRENT_DAY + timedelta(
            days=borrowing_days_total
        )

        self.borrowing.save()

        expected_price_in_cents = count_total_price(self.borrowing)
        total_price_in_cents = 11691

        self.assertEqual(expected_price_in_cents, total_price_in_cents)

    def test_create_payment_without_fine(self):
        borrowing_days = 2
        self.borrowing.actual_return_date = CURRENT_DAY + timedelta(
            days=borrowing_days
        )

        self.borrowing.save()

        session = Mock()
        session.url = "https://checkout.stripe.com/c/pay/cs_test"
        session.id = "cs_test"

        payment = create_payment(self.borrowing, session)

        self.assertEqual(payment.type, "PAYMENT")

    def test_create_payment_with_fine(self):
        borrowing_days = 6
        self.borrowing.actual_return_date = CURRENT_DAY + timedelta(
            days=borrowing_days
        )

        self.borrowing.save()

        session = Mock()
        session.url = "https://checkout.stripe.com/c/pay/cs_test"
        session.id = "cs_test"

        payment = create_payment(self.borrowing, session)

        self.assertEqual(payment.type, "FINE")
