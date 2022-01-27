from rest_framework.pagination import LimitOffsetPagination


class LimitPagination(LimitOffsetPagination):
    page_size_query_param = 'limit'
    offset_query_param = "start"