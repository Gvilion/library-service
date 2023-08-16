from rest_framework import serializers
from django.core.exceptions import ValidationError

from books.models import Book


class BookSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        data = super(BookSerializer, self).validate(attrs=attrs)
        Book.validate_inventory(
            attrs["inventory"],
            ValidationError,
        )
        return data

    class Meta:
        model = Book
        fields = "__all__"
