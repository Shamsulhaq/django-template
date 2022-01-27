from django_filters import rest_framework as filters


class BaseOrderBy(filters.FilterSet):
    order_by = filters.CharFilter(method="order_by_filter")

    def order_by_filter(self, qs, name, value):
        return qs.order_by(value)