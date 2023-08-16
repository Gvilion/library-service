import datetime

from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError

from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book,
                             on_delete=models.CASCADE,
                             related_name="borrowings")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name="borrowings")

    @property
    def is_active(self):
        return self.actual_return_date is None

    class Meta:
        ordering = ["expected_return_date"]

    def __str__(self) -> str:
        return str(self.borrow_date)
