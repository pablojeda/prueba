from django.contrib import admin
from django.urls import path, include
from rest_framework.schemas import get_schema_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('staticdata.urls')),
    path('api/docs', get_schema_view(
        title="Fever Code Challenge Pablo Ojeda",
        description="API for getting active events",
        version="1.0.0"
    ), name='openapi-schema')
]
