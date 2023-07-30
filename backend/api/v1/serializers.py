import base64
import webcolors

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers

from .utils import is_followed
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    RecipeIngredient
)

User = get_user_model()


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


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
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        exclude = ('recipe',)


class IngredientMakeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeWatchSerializer(serializers.ModelSerializer):
    author = FollowUserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        read_only=True,
        many=True,
        source='recipeingredient_set'
    )
    tags = TagSerializer(read_only=True, many=True)
    text = serializers.CharField(read_only=True, source='description')
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        if obj in Recipe.objects.filter(favorited__user=user):
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        if obj in Recipe.objects.filter(in_cart__user=user):
            return True
        return False

    class Meta:
        model = Recipe
        exclude = ('description',)


class RecipeMakeSerializer(serializers.ModelSerializer):
    ingredients = IngredientMakeSerializer(many=True)
    tags = serializers.SlugRelatedField(
        slug_field='id',
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField(required=False, allow_null=True)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        user = self.context.get('request').user
        recipe = Recipe.objects.create(author=user, **validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            current_ingredient = Ingredient.objects.get(
                id=ingredient.get('id')
            )
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=ingredient.get('amount')
            )
        return recipe

    # TODO: Рефакторинг
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.description = validated_data.get(
            'description', instance.description
        )
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        if ingredients:
            for ingredient in ingredients:
                current_ingredient = Ingredient.objects.get(
                    id=ingredient.get('id')
                )
                defaults = {
                    'amount': ingredient.get('amount')
                }
                RecipeIngredient.objects.update_or_create(
                    recipe=instance,
                    ingredient=current_ingredient,
                    defaults=defaults
                )
        if tags:
            instance.tags.set(tags)

        instance.save()
        return instance

    def to_representation(self, instance):
        context = {
            'request': self.context.get('request')
        }
        return RecipeWatchSerializer(
            context=context
        ).to_representation(instance)

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)

    def validate_name(self, value):
        user = self.context.get('request').user
        name = value
        if Recipe.objects.filter(
            author=user, name=name
        ).exists():
            raise serializers.ValidationError(
                'Нельзя создать 2 рецепта с одинаковым именем'
            )
        return value
