from django.contrib.auth.models import AbstractUser
from django.db import models

from api.v1.constants import COMMON_FIELD_LENGTH as LEN


class User(AbstractUser):
    """Расширение класса User."""
    username = models.CharField(
        max_length=LEN,
        verbose_name='Юзернейм',
    )
    first_name = models.CharField(
        max_length=LEN,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=LEN,
        verbose_name='Фамилия',
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Email-адрес',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['-created']


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name="Подписчик",
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name="Автор",
    )

    def __str__(self):
        return f'{self.user}, {self.following}'

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'], name='user_follow_author'
            )
        ]
        ordering = ['-user__created']
