from django.contrib.auth import get_user_model

from recipes.models import Recipe
from .utils import is_followed

User = get_user_model()


def validate_follow(user, follow):
    if user == follow:
        return False
    if is_followed(user, follow):
        return False
    return True


def validate_favorite(user, recipe):
    if recipe in Recipe.objects.filter(favorited__user=user):
        return False
    return True


def validate_cart(user, recipe):
    if recipe in Recipe.objects.filter(in_cart__user=user):
        return False
    return True
