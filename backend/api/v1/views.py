from django.contrib.auth import get_user_model
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework import (
    viewsets,
    permissions,
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
    RecipeMakeSerializer,
    RecipeWatchSerializer,
    RecipeFavoriteSerializer,
    TagSerializer,
    IngredientSerializer,
    FollowRecipeUserSerializer
)
from .utils import (
    custom_get_queryset,
    create_delete_related_model,
    export_pdf
)

User = get_user_model()


class NewUserViewSet(UserViewSet):
    pagination_class = CustomPageNumberPagination

    @action(["post", "delete"], detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def subscribe(self, request, *args, **kwargs):
        id = kwargs.get('id', None)
        return create_delete_related_model(
            request=request,
            serializer=FollowRecipeUserSerializer,
            validate=validate_follow,
            model=User,
            related_model=Follow,
            id=id,
            field='following',
            recipes_count=True
        )

    @action(["get"], detail=False,
            permission_classes=(permissions.IsAuthenticated,),)
    def subscriptions(self, request, *args, **kwargs):
        user = self.request.user
        queryset = self.paginate_queryset(
            User.objects.filter(following__user=user).annotate(
                recipes_count=Count("recipes")
            )
        )
        recipes_limit = request.query_params.get('recipes_limit', None)
        if recipes_limit:
            recipes_limit = int(recipes_limit)
        context = {
            'request': request,
            'recipes_limit': recipes_limit
        }
        serializer = FollowRecipeUserSerializer
        return self.get_paginated_response(
            serializer(queryset, context=context, many=True).data
        )


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (AuthorOrAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return custom_get_queryset(self.request)

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeWatchSerializer
        return RecipeMakeSerializer

    @action(["post", "delete"], detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def favorite(self, request, *args, **kwargs):
        id = kwargs.get('pk', None)
        return create_delete_related_model(
            request=request,
            serializer=RecipeFavoriteSerializer,
            validate=validate_favorite,
            model=Recipe,
            related_model=Favorite,
            id=id,
            field='recipe'
        )

    @action(["post", "delete"], detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def shopping_cart(self, request, *args, **kwargs):
        id = kwargs.get('pk', None)
        return create_delete_related_model(
            request=request,
            serializer=RecipeFavoriteSerializer,
            validate=validate_cart,
            model=Recipe,
            related_model=ShoppingCart,
            id=id,
            field='recipe'
        )

    # TODO:
    @action(["get"], detail=False,
            permission_classes=(permissions.IsAuthenticated,))
    def download_shopping_cart(self, request, *args, **kwargs):
        return export_pdf(request)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = CustomPageNumberPagination


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name', '$name')
