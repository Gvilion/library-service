from django.db import models


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
    borrowing_id = models.ForeignKey(
        to="Borrowing",
        related_name="payments",
        on_delete=models.CASCADE,
    )
    session_url = models.URLField()
    session_id = models.CharField(max_length=63, unique=True)
    money_to_pay = models.DecimalField(models.DecimalField(max_digits=10, decimal_places=2))

    def __str__(self):
        return f"Payment {self.id} ({self.type}) {self.user.email}"