from http import HTTPStatus

from rest_framework.test import APIClient
import pytest

from recipes.models import Recipe

IS_SUBSCRIBE_FIELD = 'is_subscribed'


@pytest.mark.django_db()
class Test01Recipes:

    def test_00_recipes_view(self, user_client, recipe):
        url = '/api/v1/recipes/'
        client = APIClient()
        response = user_client.get(url)
        data = response.json()
        anon_response = client.get(url)
        anon_data = anon_response.json()

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт {url} не найден'
        )
        assert response.status_code == HTTPStatus.OK, (
            f'Проверьте статус ответа эндпоинта {url}'
        )

        assert anon_response.status_code == HTTPStatus.OK, (
            f'Проверьте статус ответа эндпоинта {url}'
        )
