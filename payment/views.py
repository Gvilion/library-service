from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from payment.models import Payment
from payment.permissions import IsAdminOrIfAuthenticatedReadOnly
from payment.serializers import (
    PaymentSerializer,
    PaymentListSerializer,
    PaymentDetailSerializer,
)


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly, ]

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list":
            queryset = Payment.objects.select_related("user", "borrowing")

            if not self.request.user.is_staff:
                queryset = queryset.filter(user=self.request.user)

        if self.action == "retrieve":
            queryset = Payment.objects.select_related("user", "borrowing")

        return queryset

    def get_serializer_class(self):
        serializer_class = self.serializer_class

        if self.action == "list":
            serializer_class = PaymentListSerializer
        elif self.action == "retrieve":
            serializer_class = PaymentDetailSerializer

        return serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SuccessPaymentView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get("pk")

        payment = Payment.objects.filter(user_id=user_id).first()

        if payment:
            payment.status = "PAID"
            payment.save()

            return Response(
                {"message": "Borrowing returned successfully"},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "Payment not found or already processed"},
                status=status.HTTP_400_BAD_REQUEST
            )


class CancelPaymentView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(
            {"message": "Payment can be paid a bit later"},
            status=status.HTTP_200_OK
        )
