from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Ingredient
from .serializers import IngredientSerializer
from decimal import Decimal, InvalidOperation

# Deduct Amount from Ingredient (Internal Helper)
def deduct_inventory_internal(user, ingredient_id, req_amount):
    """Deduct a specified amount from an ingredient's quantity."""
    try:
        ingredient = Ingredient.objects.get(pk=ingredient_id, user=user)
        try:
            amount = float(req_amount)
        except (TypeError, ValueError):
            return Response({"error": "Amount must be a valid number."}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({"error": "Amount must be positive."}, status=status.HTTP_400_BAD_REQUEST)

        if ingredient.quantity < amount:
            return Response({"error": "Not enough inventory to deduct."}, status=status.HTTP_400_BAD_REQUEST)

        ingredient.quantity -= amount
        ingredient.save()
        return Response({"message": "Inventory added.", "new_quantity": float(ingredient.quantity)})

    except Ingredient.DoesNotExist:
        return Response({"error": "Ingredient Not Found."}, status=status.HTTP_404_NOT_FOUND)

# Create Ingredient View
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

# Get Ingredient View
class IngredientDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = IngredientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # only show ingredients for logged in user
        return Ingredient.objects.filter(user=self.request.user)

# Add Amount to Ingredient
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_inventory(request, pk):
    """Add a specified amount to an ingredient's quantity."""
    try:
        ingredient = Ingredient.objects.get(pk=pk, user=request.user)
        try:
            amount = float(request.data.get("amount"))
        except (TypeError, ValueError):
            return Response({"error": "Amount must be a valid number."}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({"error": "Amount must be positive."}, status=status.HTTP_400_BAD_REQUEST)

        ingredient.quantity += amount
        ingredient.save()
        return Response({"message": "Inventory added.", "new_quantity": float(ingredient.quantity)})

    except Ingredient.DoesNotExist:
        return Response({"error": "Ingredient Not Found."}, status=status.HTTP_404_NOT_FOUND)

# Deduct Amount from Ingredient (API View)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def deduct_inventory(request, pk):
    """Deduct a specified amount from an ingredient's quantity via HTTP POST."""
    amount = request.data.get("amount")

    result = deduct_inventory_internal(request.user, pk, amount)

    if "error" in result:
        return Response({"error": result["error"]}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "Inventory deducted.", "new_quantity": result["new_quantity"]}, status=200)