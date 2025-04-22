from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from inventory.models import Ingredient
from .models import Recipe, RecipeIngredient
from rest_framework import status
from decimal import Decimal

# Testing suite for Recipes including tests for creating, reading, updating, and deleting
class RecipeTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="baker", password="testpass")
        # force authenticate the user created
        self.client.force_authenticate(user=self.user)

        self.flour = Ingredient.objects.create(
            user=self.user,
            name="Flour",
            quantity=1000,
            unit="grams",
            cost=3.00,
            expiration_date="2025-12-31",
            low_stock_threshold=200
        )

        self.sugar = Ingredient.objects.create(
            user=self.user,
            name="Sugar",
            quantity=1000,
            unit="grams",
            cost=2.50,
            expiration_date="2025-12-31",
            low_stock_threshold=200
        )

        self.recipe_data = {
            "name": "Test Cake",
            "description": "A cake that tests!",
            "servings": 12,
            "ingredients": [
                {"ingredient": self.flour.id, "amount": 350, "unit": "grams"},
                {"ingredient": self.sugar.id, "amount": 150, "unit": "grams"},
            ]
        }

    def test_create_recipe(self):
        """Test creating a recipe with multiple nested ingredients and validate the link."""
        response = self.client.post('/api/recipes/', self.recipe_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipe.objects.count(), 1)
        self.assertEqual(Recipe.objects.get().name, "Test Cake")

        # ensure both ingredients were properly attached to recipe
        recipe = Recipe.objects.get()
        recipe_ingredients = RecipeIngredient.objects.filter(recipe=recipe)
        self.assertEqual(recipe_ingredients.count(), 2)
        ingredient_ids = [ri.ingredient.id for ri in recipe_ingredients]
        self.assertIn(self.flour.id, ingredient_ids)
        self.assertIn(self.sugar.id, ingredient_ids)

    def test_list_user_recipes(self):
        """Test that only recipes belonging to the authenticated user are returned."""
        self.client.post('/api/recipes/', self.recipe_data, format='json')
        other_user = User.objects.create_user(username="otheruser", password="pass123")
        Recipe.objects.create(user=other_user, name="Other Cake", description="Another testing cake", servings=2)
        response = self.client.get("/api/recipes/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Test Cake")

    def test_invalid_recipe_missing_field(self):
        """Test that recipe creation fails if a required field is missing."""
        invalid_data = self.recipe_data.copy()
        invalid_data.pop("name")
        response = self.client.post('/api/recipes/', invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recipe_requires_authentication(self):
        """Test that accessing the recipe list without authentication is not allowed."""
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/recipes/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_recipe_detail(self):
        """Test retrieving the details of a single recipe by ID."""
        post_response = self.client.post("/api/recipes/", self.recipe_data, format='json')
        recipe_id = post_response.data['id']
        get_response = self.client.get(f"/api/recipes/{recipe_id}")
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data['name'], "Test Cake")

    def test_delete_recipe(self):
        """Test deleting a recipe and confirm it is removed from the database."""
        post_response = self.client.post("/api/recipes/", self.recipe_data, format='json')
        recipe_id = post_response.data['id']
        delete_response = self.client.delete(f"/api/recipes/{recipe_id}")
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Recipe.objects.count(), 0)

    def test_update_recipe(self):
        """Test partially updating a recipe's fields via PATCH request."""
        post_response = self.client.post("/api/recipes/", self.recipe_data, format='json')
        recipe_id = post_response.data['id']
        update_data = {"name": "Updated Cake", "description": "Just an updated testing cake", "servings": 6}
        patch_response = self.client.patch(f"/api/recipes/{recipe_id}", update_data, format='json')
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['name'], "Updated Cake")

    def test_recipe_str_method(self):
        """Test that the string representation of Recipe returns the name."""
        recipe = Recipe.objects.create(user=self.user, name="Quick Bread", description="Simple bread", servings=4)
        self.assertEqual(str(recipe), "Quick Bread (4 servings)")

    def test_recipe_ingredient_str_method(self):
        """Test string representation of RecipeIngredient shows readable link."""
        recipe = Recipe.objects.create(user=self.user, name="Bread", description="", servings=4)
        ri = RecipeIngredient.objects.create(recipe=recipe, ingredient=self.flour, amount=250, unit="g")
        self.assertEqual(str(ri), f"250 g of {self.flour.name} in {recipe.name}")

    def test_calculate_cost_fields(self):
        """Test that total_cost and cost_per_serving are calculated correctly."""
        response = self.client.post("/api/recipes/", self.recipe_data, format='json')
        recipe_id = response.data['id']
        get_response = self.client.get(f"/api/recipes/{recipe_id}")

        self.assertEqual(get_response.status_code, 200)
        self.assertIn("total_cost", get_response.data)
        self.assertIn("cost_per_serving", get_response.data)
        self.assertIsInstance(get_response.data["total_cost"], float)
        self.assertIsInstance(get_response.data["cost_per_serving"], float)

        self.assertEqual(get_response.data["total_cost"], 1.42)
        self.assertEqual(get_response.data["cost_per_serving"], 0.12)

    def test_warning_when_ingredient_data_is_invalid(self):
        """Test that a warning is returned when an ingredient has invalid quantity or cost."""
        # Intentionally break one ingredient
        self.flour.quantity = 0
        self.flour.save()

        # Post recipe data
        response = self.client.post("/api/recipes/", self.recipe_data, format='json')
        recipe_id = response.data['id']
        get_response = self.client.get(f"/api/recipes/{recipe_id}")

        # Detect warnings
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertIn("warnings", get_response.data)
        self.assertGreaterEqual(len(get_response.data["warnings"]), 1)
        self.assertIn("Flour", get_response.data["warnings"][0])

    def test_cost_per_serving_zero_servings(self):
        """Test that cost_per_serving returns 0.0 when servings is zero (ZeroDivisionError)."""
        self.recipe_data["servings"] = 0
        response = self.client.post("/api/recipes/", self.recipe_data, format='json')
        recipe_id = response.data['id']
        get_response = self.client.get(f"/api/recipes/{recipe_id}")

        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data["cost_per_serving"], 0.0)



