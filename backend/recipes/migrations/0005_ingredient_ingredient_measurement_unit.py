# Generated by Django 4.2.3 on 2023-07-30 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_shoppingcart_shoppingcart_user_cart_recipe'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='ingredient',
            constraint=models.UniqueConstraint(fields=('name', 'measurement_unit'), name='ingredient_measurement_unit'),
        ),
    ]