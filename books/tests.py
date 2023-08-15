from django.contrib.auth import get_user_model
from django.test import TestCase
from decimal import Decimal

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from .models import Book


BOOKS_URL = "/api/books/"


class BookModelTestCase(TestCase):

    def setUp(self):
        Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=10,
            daily_fee=12.99
        )

    def test_book_creation(self):
        book = Book.objects.get(title="Test Book")
        self.assertEqual(book.author, "Test Author")
        self.assertEqual(book.cover, "HARD")
        self.assertEqual(book.inventory, 10)
        self.assertEqual(book.daily_fee, Decimal("12.99"))

    def test_book_str_method(self):
        book = Book.objects.get(title="Test Book")
        self.assertEqual(str(book), "Test Book by Test Author")

    def test_unique_together_constraint(self):
        with self.assertRaises(Exception):
            Book.objects.create(
                title="Test Book",
                author="Test Author",
                cover="SOFT",
                inventory=5,
                daily_fee=9.99
            )


class SuperUserAuthTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_superuser(
            email="admin@libr.com", password="TestPass1290"
        )

        self.data = {
            "title": "BOT: Atakama Crisis",
            "author": "Max Kidruk",
            "cover": "HARD",
            "inventory": 1,
            "daily_fee": 12.99
        }
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def create_book_by_superuser(self) -> None:
        response = self.client.post(
            BOOKS_URL,
            self.data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
