from rest_framework import generics, permissions
from .models import Recipe, RecipeIngredient
from .serializers import RecipeIngredientSerializer, RecipeSerializer
from decimal import Decimal, InvalidOperation
from rest_framework.response import Response

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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data.copy()

        # Get optional profit margin input
        margin = request.query_params.get("margin")
        if margin:
            try:
                margin_decimal = Decimal(str(margin))
                total_cost = Decimal(str(data.get("total_cost", 0)))
                suggested_price = round(total_cost * (1 + margin_decimal), 2)
                data["suggested_price"] = float(suggested_price)
            except (InvalidOperation, ValueError):
                data["suggested_price"] = "Invalid margin"

        return Response(data)