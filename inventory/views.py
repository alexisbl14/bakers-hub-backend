from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Ingredient
from .serializers import IngredientSerializer
from decimal import Decimal, InvalidOperation


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
    except InvalidOperation:
        return Response({"error": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

# Deduct Amount from Ingredient
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def deduct_inventory(request, pk):
    """Deduct a specified amount from an ingredient's quantity."""
    try:
        ingredient = Ingredient.objects.get(pk=pk, user=request.user)
        try:
            amount = float(request.data.get("amount"))
        except (TypeError, ValueError):
            return Response({"error": "Amount must be a valid number."}, status=status.HTTP_400_BAD_REQUEST)

        if amount <= 0:
            return Response({"error": "Amount must be positive."}, status=status.HTTP_400_BAD_REQUEST)

        if ingredient.quanity < amount:
            return Response({"error": "Not enough inventory to deduct."}, status=status.HTTP_400_BAD_REQUEST)

        ingredient.quantity -= amount
        ingredient.save()
        return Response({"message": "Inventory added.", "new_quantity": float(ingredient.quantity)})

    except Ingredient.DoesNotExist:
        return Response({"error": "Ingredient Not Found."}, status=status.HTTP_404_NOT_FOUND)
    except InvalidOperation:
        return Response({"error": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)