import csv

from django.db.models import (
    Case,
    F,
    Q,
    Sum,
    Value,
    When
)
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient
)
from users.models import User


def is_followed(user, follow):
    if follow in User.objects.filter(following__user=user):
        return True
    return False


def custom_get_queryset(request):
    user = request.user
    tags = request.query_params.getlist('tags')
    if user.is_anonymous:
        return Recipe.objects.all().annotate(
            is_favorited=Value('0')
        ).annotate(is_in_shopping_cart=Value('0'))
    recipe_list = Recipe.objects.filter(
        favorite__user=user
    ).values_list('id', flat=True)

    shopping_cart_list = Recipe.objects.filter(
        shoppingcart__user=user
    ).values_list('id', flat=True)

    queryset = Recipe.objects.all().annotate(is_favorited=Case(
        When(
            id__in=recipe_list,
            then=Value('1')
        ),
        default=Value('0')
    )).annotate(is_in_shopping_cart=Case(
        When(
            id__in=shopping_cart_list,
            then=Value('1')
        ),
        default=Value('0')
    ))

    if tags:
        queryset = queryset.filter(Q(tags__slug__in=tags)).distinct()
    return queryset


def create_delete_related_model(request, serializer, validate,
                                model, related_model, id, field,
                                **kwargs):
    recipes_count = kwargs.get('recipes_count')
    context = {
        'request': request
    }
    if request.method == 'POST':
        user = request.user
        follow = get_object_or_404(model, id=id)
        if recipes_count:
            follow.recipes_count = len(follow.recipes.all())
        if validate(user, follow):
            data = {
                'user': user,
                field: follow
            }
            related_model.objects.create(
                **data
            )
            return Response(
                serializer(
                    follow, context=context
                ).data, status=status.HTTP_201_CREATED
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        user = request.user
        follow = get_object_or_404(model, id=id)
        data = {
            'user': user,
            field: follow
        }
        follow_obj = get_object_or_404(
            related_model,
            **data
        )
        follow_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def get_csv_data(request):
    user = request.user
    cart_list = Recipe.objects.filter(shoppingcart__user=user)
    data = RecipeIngredient.objects.filter(
        recipe__in=cart_list
    ).values(
        'ingredient__name',
        unit=F('ingredient__measurement_unit__measurement_unit')
    ).distinct().annotate(
        amount=Sum('amount')
    )
    return data


def dict_to_string(dictionary):
    ingredient = dictionary.get('ingredient__name')
    unit = dictionary.get('unit')
    amount = dictionary.get('amount')
    if ingredient and unit and amount:
        return [ingredient, unit, amount]


def export_csv(request):
    data = get_csv_data(request)
    file_name = 'your_shopping_cart.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    fields = [
        'ingredient',
        'unit',
        'amount'
    ]
    writer = csv.writer(response, delimiter=';')
    writer.writerow(fields)
    for item in data:
        row = dict_to_string(item)
        writer.writerow(row)
    return response


def create_recipe_ingredient(recipe, ingredients):
    id_list = []
    amount_dict = {}
    for ingredient in ingredients:
        id = ingredient.get('id')
        id_list.append(id)
        amount_dict[id] = ingredient.get('amount')
    ingredients = Ingredient.objects.filter(
        id__in=id_list
    )
    objs = [
        RecipeIngredient(
            recipe=recipe,
            ingredient=item,
            amount=amount_dict[item.id]
        ) for item in ingredients
    ]
    RecipeIngredient.objects.bulk_create(objs)
    return recipe


def ids_from_list(array):
    ids = []
    for item in array:
        ids.append(item.get('id'))
    return ids
