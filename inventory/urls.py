from django.urls import path
from .views import IngredientDetailView, IngredientListCreateView

urlpatterns = [
    path('ingredients/', IngredientListCreateView.as_view(), name='ingredient-list-create'),
    path('ingredients/<int:pk>', IngredientDetailView.as_view(), name='ingredient-detail'),
]