from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from .models import Ingredient
from rest_framework import status


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
        """Test that an authenticated user can create an ingredient successfully."""
        response = self.client.post('/api/inventory/ingredients/', self.ingredient_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ingredient.objects.count(), 1)
        self.assertEqual(Ingredient.objects.get().name, "Butter")

    def test_list_ingredients(self):
        """Test that the user can list their ingredients."""
        Ingredient.objects.create(user=self.user, name="Sugar", quantity=100, unit="grams", cost=1.50,
                                   expiration_date="2025-12-31", low_stock_threshold=20)
        response = self.client.get('/api/inventory/ingredients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_retrieve_ingredient_detail(self):
        """Test retrieving a single ingredient via detail view."""
        ingredient = Ingredient.objects.create(user=self.user, name="Vanilla", quantity=10, unit="ml", cost=2.50,
                                   expiration_date="2025-12-31", low_stock_threshold=5)
        get_response = self.client.get(f"/api/inventory/ingredients/{ingredient.id}/")
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data['name'], "Vanilla")

    def test_ingredient_str_method(self):
        """Test that the string representation of Ingredient returns the name."""
        ingredient = Ingredient.objects.create(user=self.user, name="Salt", quantity=50, unit="g", cost=1.00, expiration_date="2025-12-31", low_stock_threshold=10)
        self.assertEqual(str(ingredient), "Salt (50 g)")

    def test_add_amount_to_ingredient(self):
        """Test adding inventory with a valid amount updates quantity correctly."""
        ingredient = Ingredient.objects.create(user=self.user, name="Sugar", quantity=100, unit="grams", cost=1.50,
                                   expiration_date="2025-12-31", low_stock_threshold=20)
        response = self.client.post(f"/api/inventory/ingredients/{ingredient.id}/add/", { "amount": 100}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["new_quantity"], 200)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.quantity, 200)

    def test_add_amount_to_ingredient_missing_amount(self):
        """Test adding inventory with a missing amount produces an error and 400 status."""
        ingredient = Ingredient.objects.create(user=self.user, name="Sugar", quantity=100, unit="grams", cost=1.50,
                                   expiration_date="2025-12-31", low_stock_threshold=20)
        response = self.client.post(f"/api/inventory/ingredients/{ingredient.id}/add/", {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_add_amount_to_ingredient_negative_amount(self):
        """Test adding inventory with a negative amount produces an error and 400 status."""
        ingredient = Ingredient.objects.create(user=self.user, name="Sugar", quantity=100, unit="grams", cost=1.50,
                                   expiration_date="2025-12-31", low_stock_threshold=20)
        response = self.client.post(f"/api/inventory/ingredients/{ingredient.id}/add/", { "amount": -100}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_add_amount_to_ingredient_invalid_type_amount(self):
        """Test adding inventory with an amount with an invalid type produces an error and 400 status."""
        ingredient = Ingredient.objects.create(user=self.user, name="Sugar", quantity=100, unit="grams", cost=1.50,
                                   expiration_date="2025-12-31", low_stock_threshold=20)
        response = self.client.post(f"/api/inventory/ingredients/{ingredient.id}/add/", { "amount": "abc"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_add_amount_to_ingredient_does_not_exist(self):
        """Test adding to an ingredient that doesn't exist produces an error and 404 status."""
        response = self.client.post(f"/api/inventory/ingredients/3/add/", { "amount": 10}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)

    def test_deduct_ingredient_valid_amount(self):
        """Test deducting inventory with a valid amount updates quantity correctly."""
        ingredient = Ingredient.objects.create(user=self.user, name="Sugar", quantity=100, unit="grams", cost=1.50,
                                   expiration_date="2025-12-31", low_stock_threshold=20)
        response = self.client.post(f"/api/inventory/ingredients/{ingredient.id}/deduct/", { "amount": 100}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["new_quantity"], 0)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.quantity, 0)

    def test_deduct_ingredient_missing_amount(self):
        """Test deducting inventory with a missing amount produces an error and 400 status."""
        ingredient = Ingredient.objects.create(user=self.user, name="Sugar", quantity=100, unit="grams", cost=1.50,
                                   expiration_date="2025-12-31", low_stock_threshold=20)
        response = self.client.post(f"/api/inventory/ingredients/{ingredient.id}/deduct/", {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_deduct_ingredient_negative_amount(self):
        """Test deducting inventory with a negative amount produces an error and 400 status."""
        ingredient = Ingredient.objects.create(user=self.user, name="Sugar", quantity=100, unit="grams", cost=1.50,
                                   expiration_date="2025-12-31", low_stock_threshold=20)
        response = self.client.post(f"/api/inventory/ingredients/{ingredient.id}/deduct/", { "amount": -100}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_deduct_ingredient_invalid_type_amount(self):
        """Test deducting inventory with an amount with an invalid type produces an error and 400 status."""
        ingredient = Ingredient.objects.create(user=self.user, name="Sugar", quantity=100, unit="grams", cost=1.50,
                                   expiration_date="2025-12-31", low_stock_threshold=20)
        response = self.client.post(f"/api/inventory/ingredients/{ingredient.id}/deduct/", { "amount": "abc"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_deduct_ingredient_too_much(self):
        """Test deducting more than available produces an error and 400 status."""
        ingredient = Ingredient.objects.create(user=self.user, name="Sugar", quantity=100, unit="grams", cost=1.50,
                                   expiration_date="2025-12-31", low_stock_threshold=20)
        response = self.client.post(f"/api/inventory/ingredients/{ingredient.id}/deduct/", { "amount": 101}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_deduct_amount_to_ingredient_does_not_exist(self):
        """Test deducting from an ingredient that doesn't exist produces an error and 404 status."""
        response = self.client.post(f"/api/inventory/ingredients/3/deduct/", { "amount": 10}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)