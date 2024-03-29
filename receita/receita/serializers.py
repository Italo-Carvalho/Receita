from rest_framework import serializers

from receita.core.models import Ingredient, Receita, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ("id", "name")
        read_only_field = ("id",)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredient objects"""

    class Meta:
        model = Ingredient
        fields = ("id", "name")
        read_only_fields = ("id",)


class ReceitaSerializer(serializers.ModelSerializer):
    """Serializer a receita"""

    ingredients = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Ingredient.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())

    class Meta:
        model = Receita
        fields = (
            "id",
            "title",
            "ingredients",
            "tags",
            "time_minutes",
            "price",
            "link",
        )
        read_only_fields = ("id",)


class ReceitaDetailSerializer(ReceitaSerializer):
    """Serializer a receita detail"""

    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)


class ReceitaImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to receitas"""

    class Meta:
        model = Receita
        fields = ("id", "image")
        read_only_fields = ("id",)
