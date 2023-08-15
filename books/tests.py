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

        self.book1 = Book.objects.create(
            title="Inferno",
            author="Dan Brown",
            cover="SOFT",
            inventory=3,
            daily_fee=15.99
        )

        self.book2 = Book.objects.create(
            title="Angels and Demons",
            author="Dan Brown",
            cover="HARD",
            inventory=2,
            daily_fee=14.99
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

    def test_list_books_by_superuser(self) -> None:
        response = self.client.get(BOOKS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_books_by_superuser(self) -> None:
        response_book1 = self.client.get(BOOKS_URL + str(self.book1.id) + "/")
        self.assertEqual(response_book1.status_code, status.HTTP_200_OK)
        self.assertEqual(response_book1.data["title"], self.book1.title)

        response_book2 = self.client.get(BOOKS_URL + str(self.book2.id) + "/")
        self.assertEqual(response_book2.status_code, status.HTTP_200_OK)
        self.assertEqual(response_book2.data["title"], self.book2.title)

    def test_create_book_by_superuser(self) -> None:
        response = self.client.post(
            BOOKS_URL,
            self.data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_book_by_superuser(self) -> None:
        updated_data = {
            "title": "Updated Title",
            "author": "New Author",
            "cover": "SOFT",
            "inventory": 5,
            "daily_fee": 9.99
        }
        response = self.client.patch(
            BOOKS_URL + str(self.book1.id) + "/",
            updated_data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_book = Book.objects.get(id=self.book1.id)
        self.assertEqual(updated_book.title, "Updated Title")
        self.assertEqual(updated_book.author, "New Author")
        self.assertEqual(updated_book.cover, "SOFT")
        self.assertEqual(updated_book.inventory, 5)
        self.assertEqual(updated_book.daily_fee, Decimal("9.99"))

    def test_delete_book_by_superuser(self):
        response = self.client.delete(BOOKS_URL + str(self.book2.id) + "/",)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(Book.DoesNotExist):
            Book.objects.get(id=self.book2.id)


class NotAdminUserAuthTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            email="user@mail.com", password="TestPass333"
        )

        self.book1 = Book.objects.create(
            title="Inferno",
            author="Dan Brown",
            cover="SOFT",
            inventory=3,
            daily_fee=15.99
        )

        self.book2 = Book.objects.create(
            title="Angels and Demons",
            author="Dan Brown",
            cover="HARD",
            inventory=2,
            daily_fee=14.99
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

    def test_list_books_by_not_admin_user(self) -> None:
        response = self.client.get(BOOKS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_books_by_not_admin_user(self) -> None:
        response_book1 = self.client.get(BOOKS_URL + str(self.book1.id) + "/")
        self.assertEqual(response_book1.status_code, status.HTTP_200_OK)
        self.assertEqual(response_book1.data["title"], self.book1.title)

        response_book2 = self.client.get(BOOKS_URL + str(self.book2.id) + "/")
        self.assertEqual(response_book2.status_code, status.HTTP_200_OK)
        self.assertEqual(response_book2.data["title"], self.book2.title)

    def test_forbidden_create_book_by_not_admin_user(self) -> None:
        response = self.client.post(BOOKS_URL, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_book_by_not_admin_user(self) -> None:
        updated_data = {"title": "Updated Title"}
        response = self.client.patch(
            BOOKS_URL + str(self.book1.id) + "/",
            updated_data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_by_not_admin_user(self) -> None:
        response = self.client.delete(BOOKS_URL + str(self.book2.id) + "/",)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Book.objects.filter(id=self.book2.id).exists())
