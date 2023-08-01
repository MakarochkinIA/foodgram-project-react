from django.contrib import admin

from api.v1.constants import INGREDIENTS_NUMBER
from .models import (
    Tag,
    Ingredient,
    Recipe,
    Favorite,
    ShoppingCart,
    RecipeIngredient
)


@admin.display(description="Кол-во добавлений в избранное")
def in_favorite(self):
    return self.favorited.count()


@admin.display(description="Кол-во добавлений в избранное")
def ingredient_list(self):
    value = ''
    ingredients = RecipeIngredient.objects.filter(
        recipe=self
    ).values_list('ingredient__name', flat=True)[:INGREDIENTS_NUMBER]
    for ingredient in ingredients:
        value += str(ingredient)
    return value


Recipe.in_favorite = in_favorite
Recipe.ingredient_list = ingredient_list


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeTagInline(admin.TabularInline):
    model = Recipe.tags.through
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug'
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInline, RecipeTagInline]
    list_display = (
        'pk',
        'author',
        'name',
        'in_favorite',
        'ingredient_list'
    )
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags')
    empty_value_display = '-пусто-'
    exclude = ["tags"]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe',
    )
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe',
    )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'recipe',
        'ingredient',
        'amount'
    )
