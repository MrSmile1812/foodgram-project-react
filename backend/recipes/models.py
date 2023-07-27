from django.core.validators import MinValueValidator
from django.db import models

from recipes.validators import SlugValidator
from user.models import User


TEXT_LENGTH = 15
MIN_COOKING_TIME = 1
MIN_INGREDIENT = 1


class Tag(models.Model):
    name = models.CharField(
        verbose_name="Название",
        help_text="Название тэга",
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        verbose_name="Цвет",
        help_text="HEX-код цвета",
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name="Слаг",
        help_text="Имя для URL",
        unique=True,
        validators=[SlugValidator],
    )

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self) -> str:
        return self.name[:TEXT_LENGTH]


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name="Ингредиент",
        help_text="Название ингредиента",
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        help_text="Единица измерения ингредиентa",
        max_length=200,
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self) -> str:
        return f"{self.name}, {self.measurement_unit}"


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        verbose_name="Тэг",
        related_name="recipes",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор",
        related_name="recipes",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Ингредиенты",
        through="IngredientInRecipe",
        related_name="recipes",
    )
    name = models.CharField(
        verbose_name="Рецепт",
        help_text="Название рецепта",
        max_length=200,
    )
    image = models.ImageField(
        verbose_name="Фотография",
        help_text="Фотография блюда",
        upload_to="recipes/",
    )
    text = models.CharField(
        verbose_name="Описание",
        help_text="Описание рецепта",
    )
    cooking_time = models.SmallIntegerField(
        verbose_name="Время приготовления",
        help_text="Время приготовления блюда",
        validators=[MinValueValidator(MIN_COOKING_TIME)],
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-pub_date"]

    def __str__(self) -> str:
        return self.name[:TEXT_LENGTH]


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        help_text="Ингредиент",
        related_name="ingredient",
        verbose_name="Ингредиент в рецепте",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        help_text="Рецепт",
        related_name="recipe",
        verbose_name="Рецепт",
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество",
        help_text="Количество ингредиента",
        validators=[MinValueValidator(MIN_INGREDIENT)],
    )

    class Meta:
        verbose_name = "Количество ингредиентов в рецепте"
        verbose_name_plural = "Количество ингредиентов в рецепте"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="uq_recipe_ingredient",
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="Пользователь",
        related_name="favorite_user",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        help_text="Рецепт",
        related_name="favorite_recipes",
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные рецепты"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="favorite_recipe",
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="Пользователь",
        related_name="shopping_user",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        help_text="Рецепт",
        related_name="shopping_recipes",
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="recipe_in_shopping_cart",
            )
        ]
