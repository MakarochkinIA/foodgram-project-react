from django.core.files.uploadedfile import SimpleUploadedFile
import pytest

from ..constants import IMAGE_NAME, SMALL_GIF, TAG_DATA, UNIT_DATA
from recipes.models import (
    Unit,
    Ingredient,
    Recipe,
    Tag,
    RecipeIngredient
)


@pytest.fixture
def tag():
    return Tag.objects.create(**TAG_DATA)


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
