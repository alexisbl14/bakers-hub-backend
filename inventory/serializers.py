from rest_framework import serializers
from .models import Ingredient

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        # hiding user from request for security purposes
        fields = ['id', 'name', 'quantity', 'unit', 'cost', 'expiration_date', 'low_stock_threshold']

