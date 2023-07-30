from http import HTTPStatus

from rest_framework.test import APIClient
import pytest

from recipes.models import Favorite, Recipe


@pytest.mark.django_db()
class Test02Favorite:

    def test_01_favorite(self, user, user_2, user_client, recipe):
        url = f'/api/v1/recipes/{recipe.id}/favorite/'
        client = APIClient()
        favorite_count = Favorite.objects.count()
        response = user_client.post(url)
        anon_response = client.post(url)
        favorite_list = Recipe.objects.filter(favorited__user=user)
        favorite_count_created = Favorite.objects.count()

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт {url} не найден'
        )
        assert response.status_code == HTTPStatus.CREATED, (
            f'Проверьте статус ответа эндпоинта {url}'
        )
        assert anon_response.status_code == HTTPStatus.UNAUTHORIZED, (
            f'Проверьте статус ответа эндпоинта {url}'
        )
        assert favorite_count_created == favorite_count + 1, (
            'Добавление в избранное не произошло'
        )
        assert recipe in favorite_list, (
            'Добавление в избранное не произошло'
        )
        favorite_count = Favorite.objects.count()
        response = user_client.post(url)
        favorite_count_created = Favorite.objects.count()

        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Проверьте статус ответа эндпоинта {url} '
            'при повторном добавлении в избранное'
        )
        assert favorite_count_created == favorite_count, (
            'Проверьте, что нельзя добавить в избранное второй раз'
        )

    def test_02_unfavorite(self, user, user_2, user_client, recipe):
        url = f'/api/v1/recipes/{recipe.id}/favorite/'
        Favorite.objects.create(
            user=user,
            recipe=recipe
        )
        favorite_count = Favorite.objects.count()
        response = user_client.delete(url)
        favorite_count_created = Favorite.objects.count()

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт {url} не найден'
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            f'Проверьте статус ответа эндпоинта {url}'
        )
        assert favorite_count_created == favorite_count - 1, (
            'Проверьте, что можно удалить избранное'
        )
