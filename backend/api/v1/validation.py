import re

from rest_framework import serializers

from recipes.models import (
    Ingredient,
    Recipe
)

from .utils import (
    ids_from_list,
    is_followed
)


def validate_follow(user, follow):
    if user == follow:
        return False
    if is_followed(user, follow):
        return False
    return True


def validate_favorite(user, recipe):
    if recipe in Recipe.objects.filter(favorite__user=user):
        return False
    return True


def validate_cart(user, recipe):
    if recipe in Recipe.objects.filter(shoppingcart__user=user):
        return False
    return True


def validate_list_unique(items):
    return len(items) == len(set(items))


def validate_tags(tags):
    if tags and validate_list_unique(tags):
        return True
    raise serializers.ValidationError(
        'Список тегов должен быть уникальным и не пустым'
    )


def validate_ingredients(ingredients):
    if ingredients and validate_list_unique(ingredients):
        return True
    raise serializers.ValidationError(
        'Список ингредиентов должен быть уникальным и не пустым'
    )


def validate_name(context, value):
    user = context.get('request').user
    name = value
    if context.get('request').method == 'POST':
        if Recipe.objects.filter(
            author=user, name=name
        ).exists():
            raise serializers.ValidationError(
                'Нельзя создать 2 рецепта с одинаковым именем'
            )
    if not re.search('[a-zA-Zа-яёА-ЯЁ]', value):
        raise serializers.ValidationError(
            'В имени должна быть хотя бы 1 буква'
        )
    return True


def validate_gt_1(value):
    return value >= 1


def validate_amount(value):
    if validate_gt_1(value):
        return True
    raise serializers.ValidationError(
        'Количество ингредиента должно быть больше 0'
    )


def validate_cooking_time(value):
    if validate_gt_1(value):
        return True
    raise serializers.ValidationError(
        'Время приготовления должно быть больше 0'
    )


def validate_recipe(context, data):
    tags = data.get('tags')
    name = data.get('name')
    cooking_time = data.get('cooking_time')
    ingredients_id = ids_from_list(data.get('ingredients'))
    if (
        validate_ingredients(ingredients_id)
        and validate_tags(tags)
        and validate_cooking_time(cooking_time)
        and validate_name(context, name)
    ):
        return data


def validate_ingredient_amount(data):
    ingredient_id = data.get('id')
    amount = data.get('amount')
    if validate_amount(amount) and Ingredient.objects.filter(
        id=ingredient_id
    ).exists():
        return data
    raise serializers.ValidationError(
        'Не найден ингредиент'
    )
