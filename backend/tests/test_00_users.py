from http import HTTPStatus

from rest_framework.test import APIClient
import pytest

from recipes.models import Follow
from .utils import create_recipes


IS_SUBSCRIBE_FIELD = 'is_subscribed'


@pytest.mark.django_db()
class Test00IsSubscribedField:

    def test_00_is_subscribed(self, user_client):
        url = '/api/v1/users/'
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
        assert not data['results'][0][IS_SUBSCRIBE_FIELD], (
            f'Проверьте поле {IS_SUBSCRIBE_FIELD}'
        )
        assert not anon_data['results'][0][IS_SUBSCRIBE_FIELD], (
            f'Проверьте поле {IS_SUBSCRIBE_FIELD} для '
            'анонимного пользователя'
        )

    def test_01_subscribe(self, user, user_2, user_client):
        url = f'/api/v1/users/{user_2.id}/subscribe/'
        client = APIClient()
        follow_count = Follow.objects.count()
        response = user_client.post(url)
        anon_response = client.post(url)
        follow_list = user.follower.select_related().values_list(
            'following', flat=True
        )
        follow_count_created = Follow.objects.count()

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт {url} не найден'
        )
        assert response.status_code == HTTPStatus.CREATED, (
            f'Проверьте статус ответа эндпоинта {url}'
        )
        assert anon_response.status_code == HTTPStatus.UNAUTHORIZED, (
            f'Проверьте статус ответа эндпоинта {url}'
        )
        assert follow_count_created == follow_count + 1, (
            'Подписка не произошла'
        )
        assert user_2.id in follow_list, (
            'Подписка не произошла'
        )
        follow_count = Follow.objects.count()
        response = user_client.post(url)
        follow_count_created = Follow.objects.count()

        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Проверьте статус ответа эндпоинта {url} '
            'при повторной подписке'
        )
        assert follow_count_created == follow_count, (
            'Проверьте, что нельзя подписаться второй раз'
        )

        url = f'/api/v1/users/{user.id}/subscribe/'
        follow_count = Follow.objects.count()
        response = user_client.post(url)
        follow_count_created = Follow.objects.count()

        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Проверьте статус ответа эндпоинта {url} '
            'при подписке на себя'
        )
        assert follow_count_created == follow_count, (
            'Проверьте, что нельзя подписаться на себя'
        )

        url = f'/api/v1/users/{user_2.id}/'
        response = user_client.get(url)
        data = response.json()
        assert data[IS_SUBSCRIBE_FIELD], (
            f'Проверьте поле {IS_SUBSCRIBE_FIELD} после подписки'
        )

    def test_02_unsubscribe(self, user, user_2, user_client):
        url = f'/api/v1/users/{user_2.id}/subscribe/'
        Follow.objects.create(
            user=user,
            following=user_2
        )
        follow_count = Follow.objects.count()
        response = user_client.delete(url)
        follow_count_created = Follow.objects.count()

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт {url} не найден'
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            f'Проверьте статус ответа эндпоинта {url}'
        )
        assert follow_count_created == follow_count - 1, (
            'Отписка не произошла'
        )

    def test_03_subscriptions(self, user, user_2, user_client,
                              tag, ingredient):
        url = '/api/v1/users/subscriptions/'
        Follow.objects.create(
            user=user,
            following=user_2
        )
        response = user_client.get(url)

        data = response.json()
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f'Эндпоинт {url} не найден'
        )
        assert response.status_code == HTTPStatus.OK, (
            f'Проверьте статус ответа эндпоинта {url}'
        )
        assert isinstance(data, dict), (
            'Проверьте паджинацию'
        )
        assert data['results'], (
            'Проверьте ответ'
        )
        assert 'recipes' in data['results'][0], (
            'Проверьте наличие поля recipes'
        )
        assert 'recipes_count' in data['results'][0], (
            'Проверьте наличие поля recipes_count'
        )

        create_recipes(user_2, tag, ingredient)

        response = user_client.get(url)

        data = response.json()

        assert len(data['results'][0]['recipes']) == 2, (
            'Проверьте количество рецептов в ответе'
        )

        url = '/api/v1/users/subscriptions/?recipes_limit=1'
        response = user_client.get(url)

        data = response.json()

        assert len(data['results'][0]['recipes']) == 1, (
            'Проверьте фильтрацию по recipes_limit'
        )
        assert data['results'][0]['recipes_count'] == 2, (
            'Проверьте поле recipes_count'
        )
