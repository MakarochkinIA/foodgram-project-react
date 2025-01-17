from django.urls import (
    include,
    path
)
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientViewSet,
    NewUserViewSet,
    RecipeViewSet,
    TagViewSet
)

router = DefaultRouter()
router.register('users', NewUserViewSet, basename='users')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
]
