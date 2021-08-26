from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient, Receita
from receita.serializers import IngredientSerializer

INGREDIENTS_URL = reverse("receita:ingredient-list")


class PublicIngredientsApiTests(TestCase):
    """Test the publicly available ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the endpoint"""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test the private ingredients API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@italocarv.com", "test4142"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieving a list of ingrediets"""
        Ingredient.objects.create(user=self.user, name="Repolho")
        Ingredient.objects.create(user=self.user, name="Tomate")

        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_ingredient_limited_to_user(self):
        """Test that ingredients for the authetincated user are returned"""
        user2 = get_user_model().objects.create_user(
            "test2@italocarv.com", "testpass"
        )
        Ingredient.objects.create(user=user2, name="Açai")
        ingredient = Ingredient.objects.create(user=self.user, name="Cupuaçu")
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["name"], ingredient.name)

    def test_create_ingredient_successful(self):
        """Test create a new ingredient"""
        payload = {"name": "Repolho"}
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user, name=payload["name"]
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test creating a invalid ingredient fails"""
        payload = {"name": ""}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """Test filtering ingredients by those assigned to receitas"""
        ingredient1 = Ingredient.objects.create(user=self.user, name="Maçã")
        ingredient2 = Ingredient.objects.create(user=self.user, name="Peru")
        receita = Receita.objects.create(
            title="Maçã caramelizada", time_minutes=5, price=10, user=self.user
        )
        receita.ingredients.add(ingredient1)
        res = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})
        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, res.data["results"])
        self.assertNotIn(serializer2.data, res.data["results"])

    def test_retrieve_ingredient_assigned_unique(self):
        """Test filtering ingredients by assigned returns unique itens"""
        ingredient = Ingredient.objects.create(user=self.user, name="Ovos")
        Ingredient.objects.create(user=self.user, name="Queijo")
        receita1 = Receita.objects.create(
            title="Ovos cuzidos", time_minutes=30, price=8.50, user=self.user
        )
        receita1.ingredients.add(ingredient)
        receita2 = Receita.objects.create(
            title="Ovos fritos", time_minutes=20, price=5.00, user=self.user
        )
        receita2.ingredients.add(ingredient)

        res = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})
        self.assertEqual(len(res.data["results"]), 1)
