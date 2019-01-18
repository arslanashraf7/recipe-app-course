from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Ingredient, Recipe
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

    def test_create_ingredient_successful(self):
        """
        Test that ingredient is created with valid data
        """
        payload = {'name': 'Ingredient'}

        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name'],
        ).exists()

        self.assertTrue(exists)

    def test_create_invalide_ingredient_fails(self):
        """
        Test that no inbgredient is created with invalid data
        """
        payload = {'name': ''}

        res = self.client.post(INGREDIENTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retriev_ingredients_assigned_to_recipe(self):
        """
        Test refiltering ingredients by those assigned ot recipis
        """
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name='Apples'
        )
        ingredient2 = Ingredient.objects.create(
            user=self.user,
            name='Turkey'
        )
        recipe = Recipe.objects.create(
            title='Apple crumble',
            time_minutes=5,
            price=10.00,
            user=self.user

        )
        recipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
