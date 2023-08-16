from drf_spectacular.utils import (extend_schema,
                                   OpenApiParameter,
                                   OpenApiExample)
from rest_framework import viewsets

from books.models import Book
from books.permissions import IsAdminOrIfAuthenticatedReadOnly
from books.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        title = self.request.query_params.get("title")
        author = self.request.query_params.get("author")

        queryset = self.queryset

        if title:
            queryset = queryset.filter(title__icontains=title)

        if author:
            queryset = queryset.filter(author__icontains=author)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "title",
                type=str,
                description=" Filter by title(ex. ?title=book title)",
            ),
            OpenApiParameter(
                "author",
                type=str,
                description=" Filter by genres(ex. ?author=author's name)",
            ),
        ],
        examples=[
            OpenApiExample(
                name="Filter by book title",
                description="Get book with specific title.",
                value="?title=harry potter",
            ),
            OpenApiExample(
                name="Filter by book author's name",
                description="Get book with specific author.",
                value="?author=rowling",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
