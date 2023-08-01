from recipes.models import Recipe, RecipeIngredient


def response_fields_check(data):
    assert isinstance(data['tags'], list), (
        'Проверьте при сериализации тегов стоит many=True '
    )
    assert isinstance(data['ingredients'], list), (
        'Проверьте при сериализации ингредиентов стоит many=True '
    )
    assert 'is_favorited' in data, (
        'Проверьте наличие поля is_favorited'
    )
    assert 'is_in_shopping_cart' in data, (
        'Проверьте наличие поля is_in_shopping_cart'
    )
    assert 'is_subscribed' in data['author'], (
        'Проверьте наличие поля is_subscribed у автора'
    )


def create_recipes(user_2, tag, ingredient):
    recipe_data = {
        'name': 'test_recipe_3',
        'text': 'test_description',
        'cooking_time': 5
    }
    recipe_data_2 = {
        'name': 'test_recipe_4',
        'text': 'test_description',
        'cooking_time': 5
    }
    recipe = Recipe.objects.create(
        author=user_2,
        **recipe_data
    )
    recipe.tags.add(tag)
    RecipeIngredient.objects.create(
        recipe=recipe,
        ingredient=ingredient,
        amount=10
    )
    recipe_2 = Recipe.objects.create(
        author=user_2,
        **recipe_data_2
    )
    recipe_2.tags.add(tag)
    RecipeIngredient.objects.create(
        recipe=recipe_2,
        ingredient=ingredient,
        amount=10
    )
