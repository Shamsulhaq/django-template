"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.routers import DefaultRouter

from .account.urls import users_router

# swagger configurations
schema_view = get_schema_view(
    openapi.Info(
        title="Backend API",
        default_version='v1',
        description="This APIs are property of BackendTech",
        contact=openapi.Contact(email='admin@backend.com'),
        license=openapi.License(name='Backend')

    ),
    public=False,
    permission_classes=(IsAuthenticated,)
)
# end swagger schema view

router = DefaultRouter()
router.registry.extend(users_router.registry)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth', include('rest_framework.urls')),
    path('api/v1/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('api/v1/', include(router.urls)),
    # swagger urls
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api-doc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
