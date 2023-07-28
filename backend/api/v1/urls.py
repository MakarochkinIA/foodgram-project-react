from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    NewUserViewSet,
    RecipeViewSet
)

router = DefaultRouter()
router.register('users', NewUserViewSet, basename='users')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('v1/', include(router.urls)),
]
