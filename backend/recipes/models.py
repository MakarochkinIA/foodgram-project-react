from django.contrib import admin
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Имя",
    )
    color = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Цвет",
    )
    slug = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Слаг",
    )

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ['-id']


class Unit(models.Model):
    measurement_unit = models.CharField(
        max_length=150,
        verbose_name="Единица измерения",
    )

    def __str__(self):
        return self.measurement_unit

    class Meta:
        verbose_name = "Единица измерения"
        verbose_name_plural = "Единицы измерения"
        ordering = ['-id']


class Ingredient(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Имя",
    )
    measurement_unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name='ingredients',
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
        ordering = ['-id']


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name="Автор",
    )
    name = models.CharField(max_length=150, verbose_name="Имя")
    image = models.ImageField(
        upload_to=settings.MEDIA,
        null=True,
        default=None,
        verbose_name="Изображение",
    )
    description = models.TextField(verbose_name="Описание")
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
        verbose_name="Время приготовления",
    )

    def __str__(self):
        return self.name

    @admin.display(description="Кол-во добавлений в избранное")
    def in_favorite(self):
        return self.favorited.count()

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'name'], name='author_recipe_name'
            )
        ]
        ordering = ['-id']


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
        ordering = ['-id']


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name="Подписчик",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited',
        verbose_name="Рецепт",
    )

    def __str__(self):
        return f'{self.user}, {self.recipe}'

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='user_favorite_recipe'
            )
        ]
        ordering = ['-id']


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
        verbose_name="Количество",
    )

    def __str__(self):
        return f'{self.recipe}, {self.ingredient}'

    class Meta:
        verbose_name = "Рецепт-Ингредиент"
        verbose_name_plural = "Рецепт-Ингредиенты"
        ordering = ['-id']


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name="Подписчик",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_cart',
        verbose_name="Рецепт",
    )

    def __str__(self):
        return f'{self.user}, {self.recipe}'

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='user_cart_recipe'
            )
        ]
        ordering = ['-id']
