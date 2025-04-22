from http import server
from rest_framework import generics, permissions
from .models import Ingredient
from .serializers import IngredientSerializer

# Create your views here.
class IngredientListCreateView(generics.ListCreateAPIView):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()

class IngredientDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()