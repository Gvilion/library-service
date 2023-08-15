from django.core.exceptions import ValidationError
from rest_framework import serializers
from borrowings.models import Borrowing
from books.serializers import BookSerializer
from payment.serializers import PaymentSerializer
from payment.stripe_helper import create_stripe_session


class BorrowingSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

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
            "payments",
        )
        read_only_fields = ("id", "is_active", "borrow_date")

    def create(self, validated_data):
        borrowing = Borrowing.objects.create(**validated_data)
        create_stripe_session(borrowing)

        return borrowing


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
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "payments",
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
            actual_return_date=validated_data["actual_return_date"],
            user=self.context["request"].user,
        )
        book.inventory -= 1
        book.save()
        request = self.context.get("request")
        create_stripe_session(borrowing, request)

        return borrowing
