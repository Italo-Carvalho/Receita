from django.urls import path, include
from rest_framework.routers import DefaultRouter
from receita import views

# /api/receita/tags/1/
router = DefaultRouter()
router.register("tags", views.TagViewSet)
router.register("ingredients", views.IngredientViewSet)
router.register("receitas", views.ReceitaViewSet)

app_name = "receita"

urlpatterns = [path("", include(router.urls))]
