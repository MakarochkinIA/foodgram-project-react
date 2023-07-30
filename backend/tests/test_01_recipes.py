from http import HTTPStatus

from rest_framework.test import APIClient
import pytest

from .constants import RECIPE_DATA
from .utils import response_fields_check
from recipes.models import Recipe

IS_SUBSCRIBE_FIELD = 'is_subscribed'


@pytest.mark.django_db()
class Test01Recipes:

    def test_00_recipes_list_view(self, user_client, recipe):
        url = '/api/v1/recipes/'
        client = APIClient()
        response = user_client.get(url)
        data = response.json()
        anon_response = client.get(url)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт {url} не найден'
        )
        assert response.status_code == HTTPStatus.OK, (
            f'Проверьте статус ответа эндпоинта {url}'
        )

        assert anon_response.status_code == HTTPStatus.OK, (
            f'Проверьте статус ответа эндпоинта {url}'
            ' для анонимного пользователя'
        )

        assert 'results' in data, (
            f'Проверьте паджинацию эндпоинта {url}'
        )
        data = data['results'][0]
        response_fields_check(data)

    def test_01_recipes_get_view(self, user_client, recipe):
        url = f'/api/v1/recipes/{recipe.id}/'
        client = APIClient()
        response = user_client.get(url)
        anon_response = client.get(url)

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт {url} не найден'
        )
        assert response.status_code == HTTPStatus.OK, (
            f'Проверьте статус ответа эндпоинта {url}'
        )

        assert anon_response.status_code == HTTPStatus.OK, (
            f'Проверьте статус ответа эндпоинта {url}'
            ' для анонимного пользователя'
        )

    def test_02_recipes_post_view(self, user_client,
                                  tag, ingredient):
        url = '/api/v1/recipes/'
        recipe_data = RECIPE_DATA
        client = APIClient()

        recipes = Recipe.objects.count()
        response = user_client.post(url, data=recipe_data, format='json')
        recipes_created = Recipe.objects.count()

        anon_response = client.post(url, data=recipe_data, format='json')

        data = response.json()
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт {url} не найден'
        )
        assert response.status_code == HTTPStatus.CREATED, (
            f'Проверьте статус ответа эндпоинта {url}'
        )

        assert anon_response.status_code == HTTPStatus.UNAUTHORIZED, (
            f'Проверьте статус ответа эндпоинта {url}'
            ' для анонимного пользователя'
        )
        assert recipes_created == recipes + 1, (
            'Рецепт не создался'
        )
        assert isinstance(data, dict), (
            'Проверьте информацию, возвращаемую сервером'
        )
        assert isinstance(data, dict), (
            'Проверьте информацию, возвращаемую сервером'
        )
        response_fields_check(data)

        recipes = Recipe.objects.count()
        response = user_client.post(url, data=recipe_data, format='json')
        recipes_created = Recipe.objects.count()

        assert recipes_created == recipes, (
            'Проверьте, что нельзя создать 2 одинаковых рецепта'
        )

    def test_03_recipes_patch_view(self, user_client, recipe, user_2_client):
        url = f'/api/v1/recipes/{recipe.id}/'
        recipe_data = RECIPE_DATA
        recipe_fields = [
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        ]
        client = APIClient()
        response2 = user_2_client.patch(url, data=recipe_data, format='json')
        anon_response = client.patch(url, data=recipe_data, format='json')
        response = user_client.patch(url, data=recipe_data, format='json')

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт {url} не найден'
        )
        assert response.status_code == HTTPStatus.OK, (
            f'Проверьте статус ответа эндпоинта {url}'
        )

        assert anon_response.status_code == HTTPStatus.UNAUTHORIZED, (
            f'Проверьте статус ответа эндпоинта {url}'
            ' для анонимного пользователя'
        )
        assert response2.status_code == HTTPStatus.FORBIDDEN, (
            f'Проверьте статус ответа эндпоинта {url}'
            ' для анонимного пользователя'
        )
        assert response2.status_code == HTTPStatus.FORBIDDEN, (
            f'Проверьте статус ответа эндпоинта {url}'
            ' для анонимного пользователя'
        )

        data = response.json()
        assert isinstance(data, dict), (
            'Проверьте при сериализации тегов стоит many=True '
        )
        assert isinstance(data['tags'], list), (
            'Проверьте при сериализации тегов стоит many=True '
        )
        assert isinstance(data['ingredients'], list), (
            'Проверьте при сериализации ингредиентов стоит many=True '
        )
        for field in recipe_fields:
            assert field in data, (
                f'В ответе нет поля {field}'
            )

    def test_03_recipes_filter(self, user_client, user_2, recipe, recipe_2):
        urls = [
            ('/api/v1/recipes/', 2),
            ('/api/v1/recipes/?is_favorited=1', 1),
            ('/api/v1/recipes/?is_in_shopping_cart=1', 1),
            (f'/api/v1/recipes/?author={user_2.id}', 1),
            ('/api/v1/recipes/?tags=breakfast', 2),
            ('/api/v1/recipes/?tags=lunch&tags=breakfast', 2),
            (f'/api/v1/recipes/?author={user_2.id}'
             '&tags=lunch&tags=breakfast&is_favorited=1'
             '&is_in_shopping_cart=1', 1),
        ]
        for url, amount in urls:
            response = user_client.get(url)
            data = response.json()
            assert len(data['results']) == amount, (
                f'Проверьте фильтр для url: {url}'
            )
