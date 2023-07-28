from recipes.models import (
    Unit,
    Ingredient,
    Recipe,
    Tag
)

TAG_DATA = {
    'name': 'Breakfast',
    'color': '#49B64E',
    'slug': 'breakfast'
}

UNIT_DATA = {
    'measurement_unit': 'кг'
}

INGREDIENT_DATA = {
    'name': 'Breakfast',
    'measurement_unit': 'breakfast'
}

RECIPE_DATA = {
    "ingredients": [
        {
            "id": 1,
            "amount": 10
        },
        {
            "id": 2,
            "amount": 5
        }
    ],
    "tags": [1],
    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
    "name": "string25",
    "text": "string",
    "cooking_time": 1,
    "description": "test"
}

IMAGE_NAME = 'small.gif'

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)

def create_tag(data):
    return Tag.objects.create(**data)
