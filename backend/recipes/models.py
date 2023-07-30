from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=150, unique=True)
    color = models.CharField(max_length=150, unique=True)
    slug = models.CharField(max_length=150, unique=True)


class Unit(models.Model):
    measurement_unit = models.CharField(max_length=150)


# TODO: uniquetogether
class Ingredient(models.Model):
    name = models.CharField(max_length=150, unique=True)
    measurement_unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name="Мера измерения",
    )


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name="Автор",
    )
    name = models.CharField(max_length=150)
    image = models.ImageField(
        upload_to=settings.MEDIA,
        null=True,
        default=None
    )
    description = models.TextField()
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
    cooking_time = models.PositiveIntegerField()

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

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'], name='user_follow_author'
            )
        ]


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

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='user_favorite_recipe'
            )
        ]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()


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

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='user_cart_recipe'
            )
        ]
