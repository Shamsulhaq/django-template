from django_filters import rest_framework as filters

from .models import User
from ..core.filters import BaseOrderBy


class UserFilter(BaseOrderBy):
    phone = filters.CharFilter(
        field_name='phone',
        lookup_expr='icontains'
    )
    name = filters.CharFilter(
        field_name='full_name',
        lookup_expr='icontains'
    )
    email = filters.CharFilter(
        field_name='email',
        lookup_expr='icontains'
    )

    class Meta:
        model = User
        fields = ['id', 'phone', 'username', 'name', 'email', 'is_active']

