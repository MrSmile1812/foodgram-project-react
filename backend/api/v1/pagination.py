from rest_framework.pagination import PageNumberPagination


class CustomPaginator(PageNumberPagination):
    """Класс пагинации страниц."""

    page_size_query_param = "limit"
