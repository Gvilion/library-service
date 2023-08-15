import datetime

from django.core.exceptions import ValidationError
from rest_framework import serializers

from borrowings.models import Borrowing
from books.serializers import BookSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(BorrowingSerializer, self).validate(attrs=attrs)
        Borrowing.validate_date(
            attrs["expected_return_date"],
            ValidationError,
        )
        return data

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "is_active",
        )
        read_only_fields = ("id", "is_active", "borrow_date")


class BorrowingListSerializer(serializers.ModelSerializer):
    book = serializers.SlugRelatedField(many=False, read_only=True, slug_field="title")

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "is_active",
        )


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "is_active",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "borrow_date",
            "expected_return_date",
        )

    def validate(self, attrs):
        book = attrs.get("book")
        expected_return_date = attrs.get("expected_return_date")

        if book.inventory == 0:
            raise serializers.ValidationError(f"There's no more '{book.title}' books!")

        Borrowing.validate_date(
            expected_return_date,
            ValidationError,
        )
        return attrs

    def create(self, validated_data):
        book = validated_data["book"]
        borrowing = Borrowing.objects.create(
            book=book,
            expected_return_date=validated_data["expected_return_date"],
            user=self.context["request"].user,
        )
        book.inventory -= 1
        book.save()
        return borrowing


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        exclude = ("id", "actual_return_date", "expected_return_date", "book", "user", "borrow_date")

    def validate(self, attrs):
        borrowing = self.instance
        actual_return_date = attrs.get("actual_return_date")

        if borrowing.actual_return_date:
            raise serializers.ValidationError("This borrowing has already been returned.")

        return attrs

    def update(self, instance, validated_data):
        instance.actual_return_date = datetime.date.today()
        instance.book.inventory += 1
        instance.book.save()
        instance.save()
        return instance
