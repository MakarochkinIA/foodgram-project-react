from django.contrib.auth.models import AbstractUser
from django.db import models


class NewUserModel(AbstractUser):
    """Расширение класса User."""

    first_name = models.CharField('Имя', max_length=30)
    last_name = models.CharField('Фамилия', max_length=150)
    email = models.EmailField(
        verbose_name='Email-адрес',
        max_length=254,
        unique=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['-id']
