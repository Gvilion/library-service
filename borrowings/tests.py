from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book
from borrowings.models import Borrowing
from datetime import date, timedelta


BORROWINGS_URL = "/api/borrowings/"


class BorrowingModelTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@email.com", password="TestPassword123"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=5,
            daily_fee=12.99
        )
        self.borrowing_data = {
            "expected_return_date": date.today() + timedelta(days=7),
            "book": self.book,
            "user": self.user,
        }

    def test_borrowing_creation(self):
        borrowing = Borrowing.objects.create(**self.borrowing_data)
        self.assertEqual(Borrowing.objects.count(), 1)
        self.assertEqual(
            borrowing.expected_return_date,
            self.borrowing_data["expected_return_date"]
        )
        self.assertEqual(borrowing.book, self.book)
        self.assertEqual(borrowing.user, self.user)
        self.assertIsNone(borrowing.actual_return_date)
        self.assertTrue(borrowing.is_active)

    def test_borrowing_validation_invalid_expected_return_date(self):
        invalid_data = self.borrowing_data.copy()
        invalid_data["expected_return_date"] = date.today() - timedelta(days=1)
        with self.assertRaises(ValidationError):
            Borrowing.objects.create(**invalid_data)

    def test_borrowing_return(self):
        borrowing = Borrowing.objects.create(**self.borrowing_data)
        borrowing.actual_return_date = date.today()
        borrowing.save()
        self.assertFalse(borrowing.is_active)

    def test_borrowing_clean_method(self):
        borrowing = Borrowing(**self.borrowing_data)
        borrowing.clean()
        borrowing.expected_return_date = date.today() - timedelta(days=1)
        with self.assertRaises(ValidationError):
            borrowing.clean()

    def test_borrowing_str_representation(self):
        borrowing = Borrowing(**self.borrowing_data)
        self.assertEqual(str(borrowing), str(borrowing.borrow_date))


class BorrowingViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@email.com", password="TestPassword123"
        )
        self.admin_user = get_user_model().objects.create_user(
            email="admin@libr.com", password="AdminPassword777", is_staff=True
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD", inventory=5,
            daily_fee=12.99
        )
        self.borrowing = Borrowing.objects.create(
            expected_return_date=date.today() + timedelta(days=7),
            book=self.book,
            user=self.user
        )

    def test_list_borrowings_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(BORROWINGS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
