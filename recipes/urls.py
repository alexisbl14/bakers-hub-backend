from django.urls import path
from .views import RecipeDetailView, RecipeListCreateView, bake_recipe

urlpatterns = [
    path('', RecipeListCreateView.as_view(), name='recipe-list-create'),
    path('<int:pk>/', RecipeDetailView.as_view(), name='recipe-detail'),
    path('<int:pk>/bake/', bake_recipe, name='bake-recipe')
]