from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/books/", include("books.urls", namespace="books")),
    path("api/user/", include("user.urls", namespace="user")),
    path("api/", include("payment.urls", namespace="payment")),

]
