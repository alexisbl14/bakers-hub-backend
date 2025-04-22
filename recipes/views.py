from rest_framework import generics, permissions
from .models import Recipe, RecipeIngredient
from .serializers import RecipeIngredientSerializer, RecipeSerializer

# Create your views here.
class RecipeCreateView(generics.ListCreateAPIView):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    # ensure only users logged in can access the view
    permission_classes = [permissions.IsAuthenticated]

    # specify what user to be assigned
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
