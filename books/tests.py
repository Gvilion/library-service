from django.test import TestCase
from .models import Book


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
        self.assertEqual(book.daily_fee, 12.99)

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
