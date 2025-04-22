from rest_framework import serializers
from .models import Recipe, RecipeIngredient
from inventory.models import Ingredient
from decimal import Decimal, InvalidOperation

class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.ReadOnlyField(source='ingredient.name')

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'ingredient', 'ingredient_name', 'amount', 'unit']

class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True)
    total_cost = serializers.SerializerMethodField()
    cost_per_serving = serializers.SerializerMethodField()

    # warnings serializer for skipped ingredients
    warnings = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'description', 'servings', 'created_at', 'ingredients', 'total_cost', 'cost_per_serving']

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)

        for item in ingredients_data:
            RecipeIngredient.objects.create(recipe=recipe, **item)

        return recipe

    # Get total cost of the recipe
    def get_total_cost(self, obj):
        total = 0
        for item in obj.ingredients.all():
            try:
                # Converting to decimal before calculations
                # Amount of ingredient / Total amount of ingredient in inventory
                unit_cost = (Decimal(str(item.amount)) / Decimal(str(item.ingredient.quantity))) * item.ingredient.cost
                total += unit_cost
            except (ZeroDivisionError, InvalidOperation, AttributeError):
                continue
        return round(total, 2)

    # Get the cost of one serving of the recipe
    def get_cost_per_serving(self, obj):
        try:
            # Converting to decimal before calculations
            return round(self.get_total_cost(obj) / Decimal(str(obj.servings)), 2)
        except (ZeroDivisionError, InvalidOperation):
            return 0

    # Get warnings when ingredient cost calculation was skipped due to errors with quantity or cost
    def get_warnings(self, obj):
        warnings = []
        for item in obj.ingredients.all():
            try:
                amount = Decimal(str(item.amount))
                quantity = Decimal(str(item.ingredient.quantity))
                cost = item.ingredient.cost
                if quantity == 0 or cost is None:
                    raise ValueError
            except (ZeroDivisionError, InvalidOperation, AttributeError, ValueError):
                warnings.append(f"Ingredient '{item.ingredient.name}' was skipped due to invalid quantity or cost.")
        return warnings