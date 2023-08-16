from django.urls import path, include
from rest_framework import routers

from payment.views import (
    PaymentViewSet,
    SuccessPaymentView,
    CancelPaymentView,
)

router = routers.DefaultRouter()
router.register("", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "<int:pk>/success/",
        SuccessPaymentView.as_view(),
        name="payment-success"
    ),
    path(
        "<int:pk>/cancel/",
        CancelPaymentView.as_view(),
        name="payment-cancel"
    ),
]

app_name = "payment"
