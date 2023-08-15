import datetime

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowings"
    )

    @property
    def is_active(self):
        return self.actual_return_date is None

    @staticmethod
    def validate_date(expected_return_date, error_to_raise):
        if expected_return_date < datetime.date.today():
            raise error_to_raise(
                "Expected return date cannot be earlier than borrow date."
            )

    def clean(self):
        Borrowing.validate_date(self.expected_return_date, ValidationError)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.full_clean()
        return super(Borrowing, self).save(
            force_insert, force_update, using, update_fields
        )

    class Meta:
        ordering = ["expected_return_date"]

    def __str__(self) -> str:
        return str(self.borrow_date)
