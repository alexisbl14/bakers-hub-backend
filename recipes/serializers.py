from rest_framework import serializers
from .models import Recipe, RecipeIngredient
from inventory.models import Ingredient

class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.ReadOnlyField(source='ingredient.name')

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'ingredient', 'ingredient_name', 'amount', 'unit']

class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'description', 'servings', 'created_at', 'ingredients']

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)

        for item in ingredients_data:
            RecipeIngredient.objects.create(recipe=recipe, **item)

        return recipe