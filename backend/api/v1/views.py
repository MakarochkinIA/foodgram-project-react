from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, permissions, pagination

from recipes.models import Follow, Recipe
from .validation import validate_follow
from .serializers import (
    FollowUserSerializer,
    RecipeMakeSerializer,
    RecipeWatchSerializer
)

User = get_user_model()


class NewUserViewSet(UserViewSet):
    @action(["post", "delete"], detail=True,
            permission_classes=(permissions.IsAuthenticated,))
    def subscribe(self, request, *args, **kwargs):
        id = kwargs.get('id', None)
        context = {
            'subscribed': True
        }
        serializer = FollowUserSerializer
        if self.request.method == 'POST':
            user = self.request.user
            follow = get_object_or_404(User, id=id)
            validated = validate_follow(user, follow)
            if validated:
                follow_obj = Follow.objects.create(
                    user=self.request.user,
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
    def subscriptions(self, request, *args, **kwargs):
        user = self.request.user
        queryset = self.paginate_queryset(
            User.objects.filter(following__user=user)
        )
        context = {
            'subscribed': True
        }
        serializer = FollowUserSerializer
        return self.get_paginated_response(
            serializer(queryset, context=context, many=True).data
        )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeWatchSerializer
        return RecipeMakeSerializer
