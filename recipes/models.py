from django.db import models
from django.contrib.auth.models import User
from inventory.models import Ingredient

# Create your models here.
class Recipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    servings = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True) # track when recipe was created

        # to display object nicely
    def __str__(self):
        return f"{self.name} ({self.servings} servings)"

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.FloatField()
    unit = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.amount} {self.unit} of {self.ingredient.name} in {self.recipe.name}"