from django.urls import path
from .views import RecipeDetailView, RecipeListCreateView

urlpatterns = [
    path('', RecipeListCreateView.as_view(), name='recipe-list-create'),
    path('<int:pk>', RecipeDetailView.as_view(), name='recipe-detail'),
]