import datetime

from rest_framework import serializers

from borrowings.models import Borrowing
from books.serializers import BookSerializer
from payment.serializers import PaymentSerializer
from payment.stripe_helper import create_stripe_session


class BorrowingSerializer(serializers.ModelSerializer):

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
    book = serializers.SlugRelatedField(many=False,
                                        read_only=True,
                                        slug_field="title")

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
    book_title = serializers.CharField(source="book.title", read_only=True)
    book_author = serializers.CharField(source="book.author", read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "book_title",
            "book_author",
            "borrow_date",
            "expected_return_date",
        )

    def validate(self, attrs):
        book = attrs.get("book")
        expected_return_date = attrs.get("expected_return_date")

        if expected_return_date <= datetime.date.today():
            raise serializers.ValidationError("Expected return date must "
                                              "be later than borrow date.")

        if book.inventory == 0:
            raise serializers.ValidationError(
                f"There's no more '{book.title}' books!"
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
    message = serializers.CharField(
        max_length=63,
        default="Make a payment first for a successful borrowing return",
        read_only=True
    )
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "message",
            "payments",
        )
        read_only_fields = (
            "message",
            "payments",
        )

    def validate(self, attrs):
        borrowing = self.instance

        if borrowing.actual_return_date:
            raise serializers.ValidationError(
                "This borrowing has already been returned."
            )

        return attrs

    def update(self, instance, validated_data):
        instance.actual_return_date = datetime.date.today()
        instance.book.inventory += 1
        instance.book.save()
        instance.save()

        request = self.context.get("request")
        create_stripe_session(instance, request)

        return instance
