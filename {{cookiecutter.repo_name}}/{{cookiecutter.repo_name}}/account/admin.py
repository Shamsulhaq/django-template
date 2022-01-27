# at matrimony/backend/user/admin.py
from django.contrib import admin

from .models import User, UnitOfHistory, UserDeviceToken

# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'username',
        'name',
        'email',
        'phone',
        'is_phone_verified',
        'is_email_verified',
        'is_active',
        'is_deleted'
    ]
    list_filter = [
        'is_active',
        'is_staff',
        'is_deleted',
        'last_active_on',
        'date_joined',
    ]
    search_fields = [
        'id',
        'name',
        'email',
        'phone',
    ]
    list_per_page = 20

    class Meta:
        model = User


admin.site.register(UnitOfHistory)
admin.site.register(UserDeviceToken)