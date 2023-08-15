from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/borrowings/", include("borrowings.urls", namespace="borrowings")),
    path("api/books/", include("books.urls", namespace="books")),
    path("api/user/", include("user.urls", namespace="user")),
    path("api/payment/", include("payment.urls", namespace="payment")),

    path("__debug__/", include("debug_toolbar.urls")),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui"
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc"
    ),
]
