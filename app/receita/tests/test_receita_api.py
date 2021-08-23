from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Receita, Tag, Ingredient
from receita.serializers import ReceitaSerializer, ReceitaDetailSerializer


RECEITAS_URL = reverse("receita:receita-list")


def detail_url(receita_id):
    """Return receita url"""
    return reverse("receita:receita-detail", args=[receita_id])


def sample_tag(user, name="Nordeste"):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name="Batata"):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def sample_receita(user, **params):
    """Create and return a sample receita"""
    defaults = {"title": "Sample receita", "time_minutes": 10, "price": 5.00}

    defaults.update(params)

    return Receita.objects.create(user=user, **defaults)


class PublicReceitaApiTests(TestCase):
    """Test unautheticated receita API access"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(RECEITAS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateReceitaApiTests(TestCase):
    """Test unauthenticated receita API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@italocarv.com", "testpass232"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_receitas(self):
        """Test retrieving a list of receitas"""
        sample_receita(user=self.user)
        sample_receita(user=self.user)
        res = self.client.get(RECEITAS_URL)
        receitas = Receita.objects.all().order_by("-id")
        serializer = ReceitaSerializer(receitas, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_receitas_limited_to_user(self):
        """Test retrieving receitas for user"""
        user2 = get_user_model().objects.create_user(
            "test2@italocarv.com", "password212"
        )
        sample_receita(user=user2)
        sample_receita(user=self.user)
        res = self.client.get(RECEITAS_URL)
        receitas = Receita.objects.filter(user=self.user)
        serializer = ReceitaSerializer(receitas, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_receita_detail(self):
        """Test viewing a receita detail"""
        receita = sample_receita(user=self.user)
        receita.tags.add(sample_tag(user=self.user))
        receita.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(receita.id)
        res = self.client.get(url)

        serializer = ReceitaDetailSerializer(receita)
        self.assertEqual(res.data, serializer.data)
