from rest_framework import generics, permissions
from .models import Recipe, RecipeIngredient
from .serializers import RecipeIngredientSerializer, RecipeSerializer

# Create your views here.
class RecipeListCreateView(generics.ListCreateAPIView):
    serializer_class = RecipeSerializer
    # ensure only users logged in can access the view
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # only show ingredients for logged in user
        return Recipe.objects.filter(user=self.request.user)

    # specify what user to be assigned
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RecipeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # only show ingredients for logged in user
        return Recipe.objects.filter(user=self.request.user)