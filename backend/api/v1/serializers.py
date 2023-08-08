from django.db import transaction
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag
)

from .utils import (
    create_recipe_ingredient,
    is_followed
)
from .validation import (
    validate_ingredient_amount,
    validate_recipe
)


class RecipeFavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return is_followed(user, obj)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('is_subscribed',)


class FollowRecipeUserSerializer(FollowUserSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.IntegerField()

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj)[:recipes_limit]
        if not recipes:
            return []
        return RecipeFavoriteSerializer(recipes, many=True).data

    class Meta(FollowUserSerializer.Meta):
        fields = FollowUserSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class IngredientCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    def validate(self, data):
        return validate_ingredient_amount(data)


class RecipeReadSerializer(serializers.ModelSerializer):
    author = FollowUserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        read_only=True,
        many=True,
        source='recipeingredient_set'
    )
    tags = TagSerializer(read_only=True, many=True)
    text = serializers.CharField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        if obj in Recipe.objects.filter(favorite__user=user):
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        if obj in Recipe.objects.filter(
            shoppingcart__user=user
        ):
            return True
        return False

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientCreateSerializer(many=True)
    tags = serializers.SlugRelatedField(
        slug_field='id',
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(required=False, allow_null=True)
    cooking_time = serializers.IntegerField()

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        user = self.context.get('request').user
        with transaction.atomic():
            recipe = Recipe.objects.create(author=user, **validated_data)
            recipe.tags.set(tags)
            recipe = create_recipe_ingredient(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            RecipeIngredient.objects.filter(recipe=instance).delete()
            instance = create_recipe_ingredient(instance, ingredients)
            instance.tags.set(tags)
            instance.save()
        return instance

    def to_representation(self, instance):
        context = {
            'request': self.context.get('request')
        }
        return RecipeReadSerializer(
            context=context
        ).to_representation(instance)

    def validate(self, data):
        return validate_recipe(self.context, data)

    class Meta:
        model = Recipe
        fields = (
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time'
        )
