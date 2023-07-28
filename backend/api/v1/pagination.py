from rest_framework.pagination import PageNumberPagination

from django.conf import settings


class CustomPaginator(PageNumberPagination):
    """Класс пагинации страниц."""

    page_size = settings.PAGE_SIZE
    page_size_query_param = "limit"
