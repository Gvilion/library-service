from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/borrowings/", include("borrowings.urls", namespace="borrowings")),
    path("api/books/", include("books.urls", namespace="books")),
    path("api/user/", include("user.urls", namespace="user")),
    path("api/payments/", include("payment.urls", namespace="payment")),

    path("__debug__/", include("debug_toolbar.urls")),

]
