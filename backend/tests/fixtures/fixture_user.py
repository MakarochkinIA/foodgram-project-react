import pytest
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username='TestUser',
        email='testuser@foodgram.fake',
        password='1234567',
    )


@pytest.fixture
def user_2(django_user_model):
    return django_user_model.objects.create_user(
        username='TestUser2',
        email='testuser2@foodgram.fake',
        password='1234567',
    )


@pytest.fixture
def token_user(user):
    token, _ = Token.objects.get_or_create(user=user)
    return {
        'token': str(token.key),
    }


@pytest.fixture
def user_client(token_user):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token_user["token"]}')
    return client


@pytest.fixture
def user_superuser(django_user_model):
    return django_user_model.objects.create_superuser(
        username='TestSuperuser',
        email='testsuperuser@foodgram.fake',
        password='1234567',
    )


@pytest.fixture
def token_user_2(user_2):
    token, _ = Token.objects.get_or_create(user=user_2)
    return {
        'token': str(token.key),
    }


@pytest.fixture
def user_2_client(token_user_2):
    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f'Token {token_user_2["token"]}'
    )
    return client


@pytest.fixture
def token_user_superuser(user_superuser):
    token, _ = Token.objects.get_or_create(user=user_superuser)
    return {
        'token': str(token.key),
    }


@pytest.fixture
def user_superuser_client(token_user_superuser):
    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f'Token {token_user_superuser["token"]}'
    )
    return client
