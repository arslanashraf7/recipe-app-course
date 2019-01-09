from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """
    Test cases for testing the ingredeients api (public)
    """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """
        Test that login is required the access the endpoint
        """
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """
    Test private ingredients api
    """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='arslan.ashraf@admin.com',
            password='admin1234',
            name='Arslan'
         )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        """
        test retrieveing a list of IngredientSerializer
        """
        Ingredient.objects.create(user=self.user, name='Test Ingredient')
        Ingredient.objects.create(user=self.user, name='Test Ingredient 2')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_ingredients_authenticated_user(self):
        """
        Test ingredients for the authenticated user are returned
        """
        user2 = get_user_model().objects.create_user(
            email='test@admin.com',
            password='admin1234',
            name='Arlana'
        )
        Ingredient.objects.create(user=user2, name='Ingredient1')
        ingredient = Ingredient.objects.create(user=self.user, name='Ingre2')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
