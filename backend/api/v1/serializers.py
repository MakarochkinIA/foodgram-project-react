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


class FollowUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, obj):
        if 'subscribed' in self.context:
            return self.context.get('subscribed')
        user = self.context.get('request').user
        if user.is_authenticated:
            return is_followed(user, obj)
        return False

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('is_subscribed',)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
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

    class Meta:
        model = Recipe
        fields = '__all__'


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
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=current_ingredient,
                    amount=ingredient.get('amount')
                )
        if tags:
            instance.tags.set(tags)

        instance.save()
        return instance

    def to_representation(self, instance):
        context = {
            'subscribed': False
        }
        return RecipeWatchSerializer(
            context=context
        ).to_representation(instance)

    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ('author',)
