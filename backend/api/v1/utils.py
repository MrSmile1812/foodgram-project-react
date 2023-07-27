def create_shopping_cart_file(ingredients):
    """Загрузка списка покупок с ингредиентами."""
    shopping_list = "Список покупок: \n"
    for ingredient in ingredients:
        shopping_list += (
            f"{ingredient['ingredient__name']} - "
            f"{ingredient['amount_sum']} "
            f"({ingredient['ingredient__measurement_unit']}) \n"
        )
    return shopping_list
