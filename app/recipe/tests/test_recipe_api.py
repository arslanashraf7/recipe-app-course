from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe

from recipe.serializers import RecipeSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **params):
    """
    Create and return a sample recipe
    """
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 5,
        'price': 5
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeAPiTests(TestCase):
    """
    Test unauthenticated recipe api access
    """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """
        Test that authentication is required
        """
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """
    Test the api with proper authentication
    """
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'arslan.ashraf@admin.com',
            'admin1234',
        )

        self.client.force_authenticate(self.user)

    def test_retrieve_recipies(self):
        """
        Test retrive the list of recipes for authenticated user
        """
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipies_limitedto_user(self):
        """
        Test the recipies according to  the user
        """
        user2 = get_user_model().objects.create_user(
            'testuser@admin.com',
            'admin1234'
        )
        sample_recipe(user2)
        sample_recipe(self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
