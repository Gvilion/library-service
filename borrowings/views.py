from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.permissions import IsAdminOrIfAuthenticatedReadCreateOnly
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
)
from payment.models import Payment

from borrowings.borrowings_documentation import (borrowings_parameters,
                                                 borrowings_examples)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadCreateOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        if self.action == "return_borrowing":
            return BorrowingReturnSerializer

        return BorrowingSerializer

    def get_queryset(self):
        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")
        queryset = Borrowing.objects.select_related("book")

        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)

        if user_id:
            if self.request.user.is_staff:
                queryset = queryset.filter(user_id=user_id)

        if is_active is not None:
            if is_active in ["false", "False", "FALSE", 0]:
                is_active = False
            elif is_active in ["true", "True", "TRUE", 1]:
                is_active = True
            queryset = queryset.filter(
                actual_return_date__isnull=bool(is_active)
            )
        return queryset

    @action(
        methods=["PATCH"],
        detail=True,
        url_path="return",
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def return_borrowing(self, request, pk=None):
        """Endpoint for returning a book"""
        user = self.request.user
        borrowing = self.get_object()
        serializer = self.get_serializer(instance=borrowing, data=request.data)

        if serializer.is_valid():
            payment_pending = Payment.objects.filter(
                user=user, borrowing=borrowing, status="PENDING"
            ).first()

            if payment_pending:
                raise serializers.ValidationError(
                    f"You have to pay before returning the book. "
                    f"Please pay via this link: {payment_pending.session_url}"
                )

            serializer.save()
            borrowing.actual_return_date = serializer.validated_data.get(
                "actual_return_date"
            )
            borrowing.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        user = self.request.user

        has_pending_payments = Payment.objects.filter(
            user=user, status="PENDING"
        ).exists()
        if has_pending_payments:
            raise serializers.ValidationError(
                "You have pending payments. Please pay them before borrowing."
            )

        serializer.save(user=user)

    @extend_schema(
        parameters=borrowings_parameters,
        examples=borrowings_examples
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
