from django.contrib import admin

from .models import (
    Follow,
    Tag,
    Ingredient,
    Recipe,
    Unit,
    Favorite,
    ShoppingCart,
    RecipeIngredient
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeTagInline(admin.TabularInline):
    model = Recipe.tags.through
    extra = 1


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'following',
    )


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


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'measurement_unit',
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeIngredientInline, RecipeTagInline]
    list_display = (
        'pk',
        'author',
        'name',
        'in_favorite'
    )
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
