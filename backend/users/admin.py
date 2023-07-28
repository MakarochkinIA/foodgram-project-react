from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import NewUserModel


@admin.register(NewUserModel)
class NewUserModelAdmin(UserAdmin):
    pass
