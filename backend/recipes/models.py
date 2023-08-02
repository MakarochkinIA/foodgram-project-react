from colorfield.fields import ColorField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.db import models

from api.v1.constants import COMMON_FIELD_LENGTH as LEN
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=LEN,
        unique=True,
        verbose_name="Имя",
    )
    color = ColorField(
        unique=True,
        verbose_name="Цвет",
    )
    slug = models.CharField(
        max_length=LEN,
        unique=True,
        verbose_name="Слаг",
    )

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ['-slug']


class Ingredient(models.Model):
    name = models.CharField(
        max_length=LEN,
        unique=True,
        verbose_name="Имя",
    )
    measurement_unit = models.CharField(
        max_length=LEN,
        verbose_name="Мера измерения",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='ingredient_measurement_unit'
            )
        ]
        indexes = [
            models.Index(fields=["name"], name="name_idx"),
        ]
        ordering = ['-name']


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name="Автор",
    )
    name = models.CharField(max_length=200, verbose_name="Имя")
    image = models.ImageField(
        upload_to=settings.MEDIA,
        null=True,
        default=None,
        verbose_name="Изображение",
    )
    text = models.TextField(verbose_name="Описание")
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='ingredient_recipe',
        verbose_name="Ингредиент",
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='tag_recipe',
        verbose_name="Тег",
    )
    cooking_time = models.PositiveIntegerField(
        validators=(
            MinValueValidator(1, 'Минимальная время готовки - 1'),
            MaxValueValidator(10, 'Максимальное время готовки - 43800 (месяц)')
        ),
        verbose_name="Время приготовления",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'name'], name='author_recipe_name'
            )
        ]
        ordering = ['-author__created']


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт"
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент"
    )
    amount = models.PositiveIntegerField(
        validators=(
            MinValueValidator(1, 'Минимальная количество - 1'),
            MaxValueValidator(10, 'Максимальное количество - 100000')
        ),
        verbose_name="Количество",
    )

    def __str__(self):
        return f'{self.recipe}, {self.ingredient}'

    class Meta:
        verbose_name = "Рецепт-Ингредиент"
        verbose_name_plural = "Рецепт-Ингредиенты"
        ordering = ['-recipe__author__created']


class AbstractFavoriteCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )

    def __str__(self):
        return f'{self.user}, {self.recipe}'

    class Meta:
        abstract = True
        ordering = ['-recipe__author__created']


class ShoppingCart(AbstractFavoriteCart):

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='user_cart_recipe'
            )
        ]


class Favorite(AbstractFavoriteCart):

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='user_favorite_recipe'
            )
        ]
