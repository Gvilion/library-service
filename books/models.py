from django.core.exceptions import ValidationError
from django.db import models


class Book(models.Model):
    CHOICES = (
        ("HARD", "Hard"),
        ("SOFT", "Soft")
    )

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=4, choices=CHOICES)
    inventory = models.PositiveIntegerField(default=1)
    daily_fee = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ("title", "author",)

    @staticmethod
    def validate_inventory(inventory, error_to_raise):
        if inventory < 0 or inventory != int(inventory):
            raise ValidationError("Inventory must be a non-negative integer.")

    def clean(self):
        Book.validate_inventory(self.inventory, ValidationError)

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.full_clean()
        return super(Book, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return f"{self.title} by {self.author}"
