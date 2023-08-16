from django.db import models
from django.utils import timezone

from user.models import User
from borrowings.models import Borrowing


class Payment(models.Model):
    STATUSES = (
        ("PENDING", "Pending"),
        ("PAID", "Paid")
    )

    TYPES = (
        ("PAYMENT", "Payment"),
        ("FINE", "Fine")
    )
    status = models.CharField(max_length=63, choices=STATUSES)
    type = models.CharField(max_length=63, choices=TYPES)
    borrowing = models.ForeignKey(
        to=Borrowing,
        related_name="payments",
        on_delete=models.CASCADE,
    )
    session_url = models.URLField()
    session_id = models.CharField(max_length=63, unique=True)
    money_to_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    user = models.ForeignKey(
        to=User,
        related_name="payments",
        on_delete=models.CASCADE,
    )

    def save(self, *args, **kwargs):
        if not self.borrowing.actual_return_date:
            days_remaining = (self.borrowing.expected_return_date
                              - timezone.now().date()).days
            self.money_to_pay = days_remaining * self.borrowing.book.daily_fee
        super(Payment, self).save(*args, **kwargs)

    def __str__(self):
        return f"Payment {self.id} ({self.type}) {self.user.email}"
