from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework import status, serializers
from rest_framework.test import APITestCase

from books.models import Book
from borrowings.models import Borrowing
from datetime import date, timedelta

from borrowings.serializers import BorrowingSerializer, BorrowingListSerializer, BorrowingDetailSerializer

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
            email="olia_user@email.com", password="TestPassword123"
        )
        self.admin_user = get_user_model().objects.create_user(
            email="olia_admin@libr.com",
            password="AdminPassword777",
            is_staff=True
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


class AuthenticatedUserBorrowingViewSetTestCase(BorrowingViewSetTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)
        Borrowing.objects.create(
            expected_return_date=date.today() + timedelta(days=3),
            book=self.book,
            user=self.user
        )

    def test_list_borrowings_authenticated(self):
        response = self.client.get(BORROWINGS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_borrowing_authenticated(self):
        data = {
            "expected_return_date": date.today() + timedelta(days=14),
            "book": self.book.id
        }
        response = self.client.post(BORROWINGS_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_return_borrowing_authenticated(self):
        borrowing = Borrowing.objects.create(
            expected_return_date=date.today() + timedelta(days=7),
            book=self.book,
            user=self.user
        )
        self.assertIsNone(borrowing.actual_return_date)
        self.assertTrue(borrowing.is_active)

        url_return = BORROWINGS_URL + str(borrowing.id) + "/return/"
        response = self.client.patch(url_return)
        borrowing.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(borrowing.actual_return_date)
        self.assertFalse(borrowing.is_active)
        borrowing.refresh_from_db()

    def test_get_queryset_authenticated_user_filtering_by_is_active_status(self):
        response = self.client.get(BORROWINGS_URL, {"is_active": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data),
            len(Borrowing.objects.filter(actual_return_date__isnull=True))
        )

    def test_get_queryset_authenticated_user_filtering_by_user_id(self):
        response = self.client.get(BORROWINGS_URL, {"user_id": self.user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data),
            len(Borrowing.objects.filter(actual_return_date__isnull=True))
        )


class NotAuthenticatedUserBorrowingViewSetTestCase(BorrowingViewSetTestCase):
    def test_list_borrowings_unauthenticated(self):
        response = self.client.get(BORROWINGS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_borrowing_unauthenticated(self):
        data = {
            "expected_return_date": date.today() + timedelta(days=14),
            "book": self.book.id
        }
        response = self.client.post(BORROWINGS_URL, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_return_borrowing_unauthenticated(self):
        borrowing = Borrowing.objects.create(
            expected_return_date=date.today() + timedelta(days=7),
            book=self.book,
            user=self.user
        )

        url_return = BORROWINGS_URL + str(borrowing.id) + "/return/"
        response = self.client.patch(url_return)
        borrowing.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIsNone(borrowing.actual_return_date)
        self.assertTrue(borrowing.is_active)


def create_test_data():
    book = Book.objects.create(
        title="Test Book",
        author="Test Author",
        cover="HARD",
        inventory=5,
        daily_fee=12.99
    )
    user = get_user_model().objects.create_user(
        email="user@email.com", password="TestPassword123"
    )
    borrowing = Borrowing.objects.create(
        expected_return_date=date.today() + timedelta(days=7),
        book=book,
        user=user
    )
    return book, borrowing


class BorrowingSerializerTestCase(APITestCase):
    def test_validate(self):
        data = {
            "expected_return_date": date.today() - timedelta(days=1)
        }
        with self.assertRaises(serializers.ValidationError):
            BorrowingSerializer(data=data).is_valid(raise_exception=True)


class BorrowingListSerializerTestCase(APITestCase):
    def test_serialize(self):
        book, borrowing = create_test_data()
        serializer = BorrowingListSerializer(instance=borrowing)
        expected_data = {
            "id": borrowing.id,
            "book": book.title,
            "borrow_date": borrowing.borrow_date.strftime("%Y-%m-%d"),
            "expected_return_date": borrowing.expected_return_date.strftime("%Y-%m-%d"),
            "actual_return_date": None,
            "is_active": True
        }
        self.assertEqual(serializer.data, expected_data)


class BorrowingDetailSerializerTestCase(APITestCase):
    def test_serialize(self):
        book, borrowing = create_test_data()
        serializer = BorrowingDetailSerializer(instance=borrowing)
        expected_data = {
            "id": borrowing.id,
            "book": {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "cover": book.cover,
                "inventory": book.inventory,
                "daily_fee": str(book.daily_fee)
            },
            "borrow_date": borrowing.borrow_date.strftime("%Y-%m-%d"),
            "expected_return_date": borrowing.expected_return_date.strftime("%Y-%m-%d"),
            "actual_return_date": None,
            "is_active": True
        }
        self.assertEqual(serializer.data, expected_data)
