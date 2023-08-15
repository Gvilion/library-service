from rest_framework import serializers

from borrowings.serializers import BorrowingListSerializer
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
    borrowing = BorrowingListSerializer(read_only=True, many=False)

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
