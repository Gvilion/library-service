from rest_framework import serializers

from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "user",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay",
        )


class PaymentListSerializer(PaymentSerializer):
    user = serializers.CharField(
        source="user.email",
        read_only=True
    )
    borrowing = serializers.CharField(
        source="borrowing.book.title",
        read_only=True
    )

    class Meta:
        model = Payment
        fields = (
            "id",
            "user",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay",
        )


class PaymentDetailSerializer(PaymentSerializer):
    user = serializers.CharField(source="user.email")
    borrowing_book = serializers.CharField(
        source="borrowing.book.title"
    )
    expected_return_date = serializers.CharField(
        source="borrowing.expected_return_date"
    )

    class Meta:
        model = Payment
        fields = (
            "id",
            "user",
            "status",
            "type",
            "borrowing_book",
            "expected_return_date",
            "session_url",
            "session_id",
            "money_to_pay",
        )
