from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Receita",
        default_version="v1",
        description="Receita is a tool to create good recipes",
        license=openapi.License(name="MIT License"),
        contact=openapi.Contact(email="italocarvalhoti@hotmail.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

api_doc_patterns = [
    path(
        "",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]

urlpatterns = [
    path("", include((api_doc_patterns, "api_doc"))),
    path("admin/", admin.site.urls),
    path(
        "api/user/",
        include("user.urls"),
    ),
    path("api/receita/", include("receita.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
