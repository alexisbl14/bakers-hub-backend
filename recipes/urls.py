from django.urls import path
from .views import RecipeListCreateView

urlpatterns = [
    path('recipes/', RecipeListCreateView.as_view(), name='recipe-list-create')
]