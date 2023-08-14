from django.db import models


class Book(models.Model):
    CHOICES = (
        ("HARD", "Hard"),
        ("SOFT", "Soft")
    )

    title = models.CharField(max_length=255, unique=True)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=4, choices=CHOICES)
    inventory = models.PositiveIntegerField(default=1)
    daily_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.title} by {self.author}"
