from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Follow


@admin.display(description="Кол-во рецептов")
def recipe_amount(self):
    return self.recipes.count()


@admin.display(description="Кол-во подписчиков")
def follow_amount(self):
    return self.follower.count()


User.recipe_amount = recipe_amount
User.follow_amount = follow_amount


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'following',
    )


@admin.register(User)
class UserModelAdmin(UserAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'recipe_amount',
        'follow_amount'
    )
    list_filter = ('email', 'username')
