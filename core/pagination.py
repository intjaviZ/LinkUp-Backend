from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"  # el front usa ?page_size=100 para dropdowns
    max_page_size = 100