import base64

from rest_framework import serializers

from django.core.files.base import ContentFile
from django.db.models import Q

from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from user.models import Follow, User


MIN_VALUE = 0


class IngredientsSerializer(serializers.ModelSerializer):
    """Список ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            "id",
            "name",
            "measurement_unit",
        )


class IngredientsInRecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор чтения ингредиентов в рецептах."""

    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)

        return super().to_internal_value(data)


class TagsSerializer(serializers.ModelSerializer):
    """Сериализация объектов типа Tags. Список тегов."""

    class Meta:
        model = Tag
        fields = (
            "id",
            "name",
            "color",
            "slug",
        )


class UserSerializer(serializers.ModelSerializer):
    """Получение данных о пользователе. И проверка подписки."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if user is None or user.is_anonymous:
            return False
        return user.follower.filter(author=obj).exists()


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализация регистрации пользователя и создания нового.
    Проверки username пользователя на валидность и уже существующего
    пользвателя.
    """

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )

    def validate(self, data):
        if data["username"] == "me":
            raise serializers.ValidationError("Недопустимое имя!")
        return data

    def user_already_created(self, data):
        data_username = data.get("username")
        data_email = data.get("email")
        if User.objects.filter(
            Q(username=data_username) | Q(email=data_email)
        ).exists():
            raise serializers.ValidationError(
                "Такой пользователь уже существует!"
            )
        return data


class ShoppingListFavoiriteSerializer(serializers.ModelSerializer):
    """Лист покупок."""

    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class FollowSerializer(serializers.ModelSerializer):
    """Сериализация подписки. Проверка подписки, получение рецептов и
    их кол-ва."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        return True

    def validate(self, data):
        author = self.instance
        user = self.context.get("request").user
        if Follow.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError("Вы уже подписаны.")
        if user == author:
            raise serializers.ValidationError(
                "Нельзя подписаться на самого себя"
            )
        return data

    def get_recipes(self, obj):
        request = self.context.get("request")
        query_params = request.query_params
        queryset = obj.recipes.all()
        if "recipes_limit" in query_params:
            recipes_limit = query_params["recipes_limit"]
            queryset = queryset[: int(recipes_limit)]
        serializer = ShoppingListFavoiriteSerializer(queryset, many=True)
        return serializer.data


class IngredientsInRecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор добавления ингредиента в рецепт."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientInRecipe
        fields = (
            "id",
            "amount",
        )


class RecipesReadSerializer(serializers.ModelSerializer):
    """Сериализация объектов типа Recipes. Чтение рецептов."""

    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    ingredients = IngredientsInRecipeReadSerializer(
        required=True, many=True, source="recipe"
    )
    tags = TagsSerializer(many=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def get_is_favorited(self, obj):
        user = self.context.get("request").user
        return (
            user.is_authenticated
            and obj.favorite_recipes.filter(user=user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user
        return (
            user.is_authenticated
            and obj.shopping_recipes.filter(user=user).exists()
        )


class RecipesWriteSerializer(serializers.ModelSerializer):
    """Сериализация объектов типа Recipes. Запись и обновление рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = IngredientsInRecipeWriteSerializer(
        many=True, source="recipe"
    )
    image = Base64ImageField()
    name = serializers.CharField(max_length=200)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
        )
        read_only_fields = ("author",)

    def validate(self, data):
        ingredients = data["recipe"]
        tags = data["tags"]
        cooking_time = data["cooking_time"]
        ingredients_list = []
        if not ingredients:
            raise serializers.ValidationError("Добавьте ингредиенты!")
        if not tags:
            raise serializers.ValidationError("Добавьте тэг!")
        for ingredient in ingredients:
            ingredient_id = ingredient["id"]
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError(
                    "Ингредиенты должны быть уникальными."
                )
            ingredients_list.append(ingredient_id)
            amount = ingredient["amount"]
            if int(amount) <= MIN_VALUE:
                raise serializers.ValidationError(
                    "Количество ингридиента не может быть меньше/равным 0!"
                )
        if int(cooking_time) <= MIN_VALUE:
            raise serializers.ValidationError(
                "Время приготовления не может быть меньше/равным 0!"
            )
        return data

    def create_update_ingredient(self, ingredients, recipe):
        IngredientInRecipe.objects.bulk_create(
            [
                IngredientInRecipe(
                    ingredient=ingredient.get("id"),
                    recipe=recipe,
                    amount=ingredient.get("amount"),
                )
                for ingredient in ingredients
            ]
        )

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("recipe")
        user = self.context.get("request").user
        recipe = Recipe.objects.create(author=user, **validated_data)
        recipe.tags.set(tags)
        self.create_update_ingredient(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags")
        instance.tags.clear()
        instance.tags.set(tags)
        ingredients = validated_data.pop("recipe")
        instance.ingredients.clear()
        self.create_update_ingredient(ingredients, instance)
        return super().update(instance, validated_data)
