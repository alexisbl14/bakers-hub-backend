from django.urls import path
from .views import IngredientDetailView, IngredientListCreateView, add_inventory, deduct_inventory

urlpatterns = [
    path('ingredients/', IngredientListCreateView.as_view(), name='ingredient-list-create'),
    path('ingredients/<int:pk>/', IngredientDetailView.as_view(), name='ingredient-detail'),
    path('ingredients/<int:pk>/add/', add_inventory, name='add-inventory'),
    path('ingredients/<int:pk>/deduct/', deduct_inventory, name='deduct-inventory'),
]