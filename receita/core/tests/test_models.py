from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from receita.core import models


def sample_user(email="test@italocarv.com", password="testpass"):
    """Crate a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    def test_user_with_email_sucess(self):
        """Test creating new user with an email is sucessful"""
        email = "test@italocarv.com"
        password = "testpassword"
        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = "test@ITALOCARVALHO.CoM"
        user = get_user_model().objects.create_user(email, "test321")

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "test231")

    def test_create_superuser(self):
        """ "Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            "test@italocarv.com", "test123"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(user=sample_user(), name="barbecue")
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string representation"""
        ingredient = models.Ingredient.objects.create(user=sample_user(), name="Batata")
        self.assertEqual(str(ingredient), ingredient.name)

    def test_receita_str(self):
        """Test the receita string representation"""
        receita = models.Receita.objects.create(
            user=sample_user(), title="strogonoff", time_minutes=5, price=5.00
        )
        self.assertEqual(str(receita), receita.title)

    @patch("uuid.uuid4")
    def test_receita_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = "test-uuid"
        mock_uuid.return_value = uuid
        file_path = models.receita_image_file_path(None, "myimage.jpg")
        exp_path = f"uploads/receita/{uuid}.jpg"
        self.assertEqual(file_path, exp_path)
