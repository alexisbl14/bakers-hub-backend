from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from .models import Ingredient
from rest_framework import status


# Create your tests here.
class IngredientTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="baker", password="testpass")
        # force authenticate the user created
        self.client.force_authenticate(user=self.user)
        self.ingredient_data = {
            "name": "Butter",
            "quantity": 200,
            "unit": "grams",
            "cost": 4.99,
            "expiration_date": "2025-12-31",
            "low_stock_threshold": 50
        }

    def test_create_ingredient(self):
        response = self.client.post('/api/inventory/ingredients/', self.ingredient_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ingredient.objects.count(), 1)
        self.assertEqual(Ingredient.objects.get().name, "Butter")

    def test_list_ingredients(self):
        Ingredient.objects.create(user=self.user, name="Sugar", quantity=100, unit="grams", cost=1.50,
                                   expiration_date="2025-12-31", low_stock_threshold=20)
        response = self.client.get('/api/inventory/ingredients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)