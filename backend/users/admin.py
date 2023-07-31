from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import NewUserModel


@admin.register(NewUserModel)
class NewUserModelAdmin(UserAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = ('email', 'username')
