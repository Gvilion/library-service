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


class PaymentListDetailSerializer(PaymentSerializer):
    user = serializers.CharField(source="user.email")
    borrowing = serializers.CharField(source="borrowing.book.title")

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
