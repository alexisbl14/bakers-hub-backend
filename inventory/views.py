from rest_framework import generics, permissions
from .models import Ingredient
from .serializers import IngredientSerializer

# Create your views here.
class IngredientListCreateView(generics.ListCreateAPIView):
    serializer_class = IngredientSerializer
    # ensure only users logged in can access the view
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # only show ingredients for logged in user
        return Ingredient.objects.filter(user=self.request.user)

    # specify what user to be assigned
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class IngredientDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()