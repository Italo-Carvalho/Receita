from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from receita.core.models import Receita, Tag
from receita.receita.serializers import TagSerializer

TAGS_URL = reverse("receita:tag-list")


class PublicTagsApiTests(TestCase):
    """Test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            "test@italocarv.com", "password23"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name="Carnes")
        Tag.objects.create(user=self.user, name="Nordeste")

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for authentiated user"""
        user2 = get_user_model().objects.create_user(
            "test2@italocarv.com", "password23"
        )
        Tag.objects.create(user=user2, name="Fruta")
        tag = Tag.objects.create(user=self.user, name="Bolos")

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), 1)
        self.assertEqual(res.data["results"][0]["name"], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {"name": "Test tag"}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(user=self.user, name=payload["name"]).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating a new tag with invalid paylaod"""
        payload = {"name": ""}
        res = self.client.post(TAGS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_receitas(self):
        """Test filtering tags by those assigned to receitas"""
        tag1 = Tag.objects.create(user=self.user, name="Aniversario")
        tag2 = Tag.objects.create(user=self.user, name="Almoço")
        receita = Receita.objects.create(
            title="Café da manha", time_minutes=10, price=5.00, user=self.user
        )
        receita.tags.add(tag1)
        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data["results"])
        self.assertNotIn(serializer2.data, res.data["results"])

    def test_retrieve_tags_assigned_unique(self):
        """Test filtering tags by assigne returns unique items"""
        tag = Tag.objects.create(user=self.user, name="Café da manhã")
        Tag.objects.create(user=self.user, name="Lanche")
        receita1 = Receita.objects.create(
            title="Panquecas", time_minutes=5, price=3.00, user=self.user
        )
        receita1.tags.add(tag)
        receita2 = Receita.objects.create(
            title="Mingau", time_minutes=3, price=2.00, user=self.user
        )
        receita2.tags.add(tag)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})
        self.assertEqual(len(res.data["results"]), 1)
