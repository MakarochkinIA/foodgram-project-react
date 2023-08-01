import django_filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class RecipeFilterSet(django_filters.rest_framework.FilterSet):
    is_favorited = django_filters.NumberFilter(
        field_name='is_favorited'
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        field_name='is_in_shopping_cart'
    )

    class Meta:
        fields = (
            'is_favorited',
            'is_in_shopping_cart',
            'author'
        )
        model = Recipe


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'
