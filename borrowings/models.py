from django.conf import settings
from django.db import models


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.IntegerField()
    # add this to the book field when Book and Borrowing are created: models.ForeignKey(Book, on_delete=models.CASCADE)

    # uncomment this when custom User model is implemented:
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    @property
    def is_active(self):
        return self.actual_return_date in None

    class Meta:
        ordering = ["expected_return_date"]

    def __str__(self) -> str:
        return str(self.actual_return_date)
