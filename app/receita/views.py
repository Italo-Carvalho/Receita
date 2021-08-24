from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from core.models import Tag, Ingredient, Receita
from receita import serializers


class BaseReceitaAttrViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin
):
    """Base viewset for user owned receita attributes"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.filter(user=self.request.user).order_by("-name")

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseReceitaAttrViewSet):
    """Manage tag in the database"""

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseReceitaAttrViewSet):
    """Manage ingredients in the database"""

    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class ReceitaViewSet(viewsets.ModelViewSet):
    """Manage receita in the database"""

    parser_classes = (MultiPartParser,)
    serializer_class = serializers.ReceitaSerializer
    queryset = Receita.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Retrieve the receitas for the authenticated user"""
        if getattr(self, "swagger_fake_view", False):
            # queryset just for schema generation metadata
            return self.queryset.none()
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return a appropriate serializer class"""
        if self.action == "retrieve":
            return serializers.ReceitaDetailSerializer

        elif self.action == "upload_image":
            return serializers.ReceitaImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new receita"""
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Upload file...",
    )
    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        """Upload an image to a receita"""
        receita = self.get_object()
        serializer = self.get_serializer(receita, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
