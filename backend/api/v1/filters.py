import django_filters
from rest_framework import filters
from recipes.models import Recipe


class RecipeFilterSet(django_filters.rest_framework.FilterSet):
    is_favorited = django_filters.NumberFilter(
        field_name='is_favorited'
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        field_name='is_in_shopping_cart'
    )
    author = django_filters.NumberFilter(
        field_name='author__id',
    )

    class Meta:
        fields = (
            'is_favorited',
            'is_in_shopping_cart',
            'author'
        )
        model = Recipe
