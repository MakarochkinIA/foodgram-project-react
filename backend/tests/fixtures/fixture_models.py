from django.core.files.uploadedfile import SimpleUploadedFile
import pytest

from ..constants import IMAGE_NAME, SMALL_GIF, TAG_DATA, UNIT_DATA
from recipes.models import (
    Unit,
    Ingredient,
    Recipe,
    Tag,
    RecipeIngredient,
    Favorite,
    ShoppingCart
)


@pytest.fixture
def tag():
    return Tag.objects.create(**TAG_DATA)


@pytest.fixture
def tag_2():
    data = {
        'name': 'Lunch',
        'color': '#7DD0D7',
        'slug': 'lunch'
    }
    return Tag.objects.create(**data)


@pytest.fixture
def unit():
    return Unit.objects.create(**UNIT_DATA)


@pytest.fixture
def ingredient(unit):
    name = 'apple'
    return Ingredient.objects.create(
        name=name,
        measurement_unit=unit
    )


@pytest.fixture
def recipe(user, ingredient, tag):
    image = SimpleUploadedFile(
        name=IMAGE_NAME,
        content=SMALL_GIF,
        content_type='image/gif',
    )
    recipe_data = {
        'name': 'test_recipe',
        'description': 'test_description',
        'cooking_time': 5
    }
    recipe = Recipe.objects.create(
        author=user,
        image=image,
        **recipe_data
    )
    recipe.tags.add(tag)
    RecipeIngredient.objects.create(
        recipe=recipe,
        ingredient=ingredient,
        amount=10
    )
    return recipe


@pytest.fixture
def recipe_2(user, user_2, ingredient, tag, tag_2):
    image = SimpleUploadedFile(
        name=IMAGE_NAME,
        content=SMALL_GIF,
        content_type='image/gif',
    )
    recipe_data = {
        'name': 'test_recipe_2',
        'description': 'test_description',
        'cooking_time': 5
    }
    recipe = Recipe.objects.create(
        author=user_2,
        image=image,
        **recipe_data
    )
    recipe.tags.set([tag, tag_2])
    RecipeIngredient.objects.create(
        recipe=recipe,
        ingredient=ingredient,
        amount=10
    )
    Favorite.objects.create(
        user=user,
        recipe=recipe
    )
    ShoppingCart.objects.create(
        user=user,
        recipe=recipe
    )
    return recipe
