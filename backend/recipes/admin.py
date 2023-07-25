from django.contrib import admin

from recipes.models import (
    Favorite,
    Ingredients,
    IngredientsInRecipes,
    Recipes,
    ShoppingCart,
    Tags,
)


@admin.register(Tags)
class TagsAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "color",
        "slug",
    )
    search_fields = (
        "name",
        "slug",
    )
    list_filter = ("name",)
    empty_value_display = "-пусто-"


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    search_fields = ("name",)
    list_filter = ("name",)
    ordering = ("name",)


@admin.register(IngredientsInRecipes)
class AmountIngredientAdmin(admin.ModelAdmin):
    list_display = (
        "ingredient",
        "recipe",
        "amount",
    )


class IngredientInRecipesAmountInline(admin.TabularInline):
    model = IngredientsInRecipes
    extra = 1
    min_num = 1


@admin.register(Recipes)
class RecipesAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
        "get_in_favorites",
    )
    list_filter = (
        "name",
        "author",
        "tags",
    )
    inlines = (IngredientInRecipesAmountInline,)
    search_fields = (
        "name",
        "author",
    )
    ordering = ("name",)
    empty_value_display = "-пусто-"

    def get_in_favorites(self, obj):
        return obj.favorite_recipes.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )
    list_filter = (
        "user",
        "recipe",
    )
    search_fields = ("user", "recipe")
    empty_value_display = "-пусто-"


@admin.register(ShoppingCart)
class BuyListAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )
    list_filter = (
        "user",
        "recipe",
    )
    search_fields = ("user",)
    empty_value_display = "-пусто-"
