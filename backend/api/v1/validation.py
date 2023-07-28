from django.contrib.auth import get_user_model

from .utils import is_followed

User = get_user_model()


def validate_follow(user, follow):
    if user == follow:
        return False
    if is_followed(user, follow):
        return False
    return True
