from datetime import timedelta

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from books.models import Book
from borrowings.models import Borrowing
from payment.models import Payment

CURRENT_DAY = timezone.now().date()
BORROWING_DAYS = 3


class PaymentModelTest(TestCase):
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

    def test_payment_str(self):
        expected_str = (
            f"Payment {self.payment.id} "
            f"({self.payment.payment_type}) {self.payment.user.email}"
        )

        self.assertEqual(expected_str, str(self.payment))

    def test_payment_money_to_pay(self):
        expected_money_to_pay = 10.88

        self.borrowing.actual_return_date = CURRENT_DAY + timedelta(days=2)
        self.borrowing.save()

        self.payment.money_to_pay = expected_money_to_pay
        self.payment.save()

        self.assertEqual(
            self.payment.money_to_pay,
            expected_money_to_pay
        )
