def response_fields_check(data):
    assert isinstance(data['tags'], list), (
        'Проверьте при сериализации тегов стоит many=True '
    )
    assert isinstance(data['ingredients'], list), (
        'Проверьте при сериализации ингредиентов стоит many=True '
    )
    assert 'is_favorited' in data, (
        'Проверьте наличие поля is_favorited'
    )
    assert 'is_in_shopping_cart' in data, (
        'Проверьте наличие поля is_in_shopping_cart'
    )
    assert 'is_subscribed' in data['author'], (
        'Проверьте наличие поля is_subscribed у автора'
    )
