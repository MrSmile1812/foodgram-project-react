from django.contrib import admin

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)


@admin.register(Tag)
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


@admin.register(Ingredient)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(IngredientInRecipe)
class AmountIngredientAdmin(admin.ModelAdmin):
    list_display = (
        "ingredient",
        "recipe",
        "amount",
    )


class IngredientInRecipesAmountInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipesAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
        "get_in_favorites",
    )
    list_filter = (
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

    def get_queryset(self, request):
        return (
            super(RecipesAdmin, self)
            .get_queryset(request)
            .prefetch_related(
                "tags",
                "ingredients",
            )
            .select_related("author")
        )

    def get_in_favorites(self, obj):
        return obj.favorite_recipes.count()


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )
    list_filter = ("user",)
    search_fields = ("user", "recipe")
    empty_value_display = "-пусто-"

    def get_queryset(self, request):
        return (
            super(FavoriteAdmin, self)
            .get_queryset(request)
            .select_related("user", "recipe")
        )


@admin.register(ShoppingCart)
class BuyListAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recipe",
    )
    list_filter = ("user",)
    search_fields = ("user", "recipe")
    empty_value_display = "-пусто-"

    def get_queryset(self, request):
        return (
            super(BuyListAdmin, self)
            .get_queryset(request)
            .select_related("user", "recipe")
        )
