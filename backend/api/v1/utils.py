from django.contrib.auth import get_user_model

User = get_user_model()


def is_followed(user, follow):
    if follow in User.objects.filter(following__user=user):
        return True
    return False
