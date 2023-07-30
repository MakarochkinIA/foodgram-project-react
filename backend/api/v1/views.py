from django.contrib.auth import get_user_model
from django.db.models import Q, Case, Value, When
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import (
    viewsets,
    permissions,
    pagination,
    filters,
)

from recipes.models import (
    Follow,
    Recipe,
    Favorite,
    ShoppingCart,
    Tag,
    Ingredient
)
from .filters import RecipeFilterSet
from .pagination import CustomPageNumberPagination
from .permissions import AuthorOrAuthenticatedOrReadOnly
from .validation import validate_follow, validate_favorite, validate_cart
from .serializers import (
    FollowUserSerializer,
    RecipeMakeSerializer,
    RecipeWatchSerializer,
    RecipeFavoriteSerializer,
    TagSerializer,
    IngredientSerializer
)

User = get_user_model()


class NewUserViewSet(UserViewSet):
    @action(["post", "delete"], detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def subscribe(self, request, *args, **kwargs):
        id = kwargs.get('id', None)
        context = {
            'request': self.request
        }
        serializer = FollowUserSerializer
        if self.request.method == 'POST':
            user = self.request.user
            follow = get_object_or_404(User, id=id)
            if validate_follow(user, follow):
                Follow.objects.create(
                    user=user,
                    following=follow
                )
                return Response(
                    serializer(
                        follow, context=context
                    ).data, status=status.HTTP_201_CREATED
                )
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if self.request.method == 'DELETE':
            user = self.request.user
            follow = get_object_or_404(User, id=id)
            follow_obj = get_object_or_404(
                Follow,
                user=user,
                following=follow
            )
            follow_obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(["get"], detail=False,
            permission_classes=(permissions.IsAuthenticated,),
            pagination_class=pagination.PageNumberPagination)
    # TODO: Вывод рецептов
    def subscriptions(self, request, *args, **kwargs):
        user = self.request.user
        queryset = self.paginate_queryset(
            User.objects.filter(following__user=user)
        )
        context = {
            'request': self.request
        }
        serializer = FollowUserSerializer
        return self.get_paginated_response(
            serializer(queryset, context=context, many=True).data
        )


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (AuthorOrAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        tags = self.request.query_params.getlist('tags')
        if user.is_anonymous:
            return Recipe.objects.all().annotate(
                is_favorited=Value('0')
            ).annotate(is_in_shopping_cart=Value('0'))
        recipe_list = Recipe.objects.filter(
            favorited__user=user
        ).values_list('id', flat=True)
        shopping_cart_list = Recipe.objects.filter(
            in_cart__user=user
        ).values_list('id', flat=True)
        queryset = Recipe.objects.all().annotate(is_favorited=Case(
            When(
                id__in=recipe_list,
                then=Value('1')
            ),
            default=Value('0')
        )).annotate(is_in_shopping_cart=Case(
            When(
                id__in=shopping_cart_list,
                then=Value('1')
            ),
            default=Value('0')
        ))
        if tags:
            for tag in tags:
                queryset = queryset.filter(Q(tags__slug=tag))
        return queryset

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeWatchSerializer
        return RecipeMakeSerializer

    @action(["post", "delete"], detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, *args, **kwargs):
        id = kwargs.get('pk', None)
        serializer = RecipeFavoriteSerializer
        if self.request.method == 'POST':
            user = self.request.user
            recipe = get_object_or_404(Recipe, id=id)
            context = {
                'request': self.request
            }
            if validate_favorite(user, recipe):
                Favorite.objects.create(
                    user=user,
                    recipe=recipe
                )
                return Response(
                    serializer(
                        recipe, context=context
                    ).data, status=status.HTTP_201_CREATED
                )
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if self.request.method == 'DELETE':
            user = self.request.user
            recipe = get_object_or_404(Recipe, id=id)
            favorite_obj = get_object_or_404(
                Favorite,
                user=user,
                recipe=recipe
            )
            favorite_obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    # TODO: Рефакторинг
    @action(["post", "delete"], detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, *args, **kwargs):
        id = kwargs.get('pk', None)
        serializer = RecipeFavoriteSerializer
        if self.request.method == 'POST':
            user = self.request.user
            recipe = get_object_or_404(Recipe, id=id)
            context = {
                'request': self.request
            }
            if validate_cart(user, recipe):
                ShoppingCart.objects.create(
                    user=user,
                    recipe=recipe
                )
                return Response(
                    serializer(
                        recipe, context=context
                    ).data, status=status.HTTP_201_CREATED
                )
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if self.request.method == 'DELETE':
            user = self.request.user
            recipe = get_object_or_404(Recipe, id=id)
            favorite_obj = get_object_or_404(
                ShoppingCart,
                user=user,
                recipe=recipe
            )
            favorite_obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    # TODO:
    @action(["get"], detail=False,
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request, *args, **kwargs):
        serializer = RecipeFavoriteSerializer
        if self.request.method == 'POST':
            user = self.request.user
            recipe = get_object_or_404(Recipe, id=id)
            if validate_favorite(user, recipe):
                ShoppingCart.objects.create(
                    user=user,
                    recipe=recipe
                )
                return Response(
                    serializer(
                        recipe,
                    ).data, status=status.HTTP_201_CREATED
                )
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if self.request.method == 'DELETE':
            user = self.request.user
            recipe = get_object_or_404(Recipe, id=id)
            favorite_obj = get_object_or_404(
                ShoppingCart,
                user=user,
                recipe=recipe
            )
            favorite_obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = pagination.PageNumberPagination


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = pagination.PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name', '$name')
