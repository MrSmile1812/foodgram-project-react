from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import exceptions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from django.db.models import Count, Sum
from django.shortcuts import HttpResponse, get_object_or_404

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from user.models import Follow, User

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPaginator
from .permissions import AuthorOrReadOnly
from .serializers import (
    FollowSerializer,
    IngredientsSerializer,
    RecipesReadSerializer,
    RecipesWriteSerializer,
    ShoppingListFavoiriteSerializer,
    TagsSerializer,
    UserSerializer,
)
from .utils import create_shopping_cart_file


class TagsViewSet(viewsets.ModelViewSet):
    """Класс для работы с моделью Tags."""

    queryset = Tag.objects.all()
    serializer_class = TagsSerializer


class IngredientsViewSet(viewsets.ModelViewSet):
    """Класс для работы с Ingredients."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = [IngredientFilter]
    search_fields = ("^name",)


class UsersViewSet(UserViewSet):
    """Класс для работы с User."""

    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all().annotate(recipes_count=Count("recipes"))

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=(IsAuthenticated,),
        url_path="me",
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=False,
        permission_classes=(IsAuthenticated,),
        pagination_class=CustomPaginator,
    )
    def subscriptions(self, request):
        user = self.request.user
        queryset = User.objects.filter(following__user=user).annotate(
            recipes_count=Count("recipes")
        )
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            page, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, pk=id)

        follow_search = Follow.objects.filter(user=user, author=author)

        if request.method == "POST":
            if user == author:
                raise exceptions.ValidationError(
                    "Подписываться на себя запрещено."
                )
            if follow_search.exists():
                raise exceptions.ValidationError(
                    "Вы уже подписаны на этого пользователя."
                )
            Follow.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "DELETE":
            if (Follow.objects.filter(user=user, author=author).delete())[
                0
            ] != 0:
                return Response(
                    status=status.HTTP_204_NO_CONTENT,
                )
            raise exceptions.ValidationError(
                "Вы не подписаны на этого пользователя."
            )


class RecipesViewSet(viewsets.ModelViewSet):
    """Класс для работы с моделью Recipes."""

    queryset = Recipe.objects.prefetch_related(
        "tags",
        "ingredients",
    ).select_related("author")
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_class = [AuthorOrReadOnly]
    pagination_class = CustomPaginator

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipesReadSerializer
        return RecipesWriteSerializer

    def post_delete_recipe(self, request, pk, model):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = self.request.user
        if request.method == "POST":
            serializer = ShoppingListFavoiriteSerializer(recipe)
            if model.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {"errors": "Рецепт  уже добавлен!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            model.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            if (model.objects.filter(user=user, recipe=recipe).delete())[
                0
            ] != 0:
                return Response(
                    status=status.HTTP_204_NO_CONTENT,
                )
            return Response(
                {"errors": "Рецепт уже убран!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        permission_class=(IsAuthenticated,),
    )
    def favorite(self, request, **kwargs):
        return self.post_delete_recipe(request, kwargs.pop("pk"), Favorite)

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        permission_class=(IsAuthenticated,),
    )
    def shopping_cart(self, request, **kwargs):
        return self.post_delete_recipe(request, kwargs.pop("pk"), ShoppingCart)

    @action(methods=["GET"], detail=False, permission_class=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = IngredientInRecipe.objects.select_related(
            "recipe", "ingredient"
        )
        ingredients = ingredients.filter(
            recipe__shopping_recipes__user=request.user
        )
        ingredients = ingredients.values(
            "ingredient__name", "ingredient__measurement_unit"
        )
        ingredients = ingredients.annotate(amount_sum=Sum("amount"))
        ingredients = ingredients.order_by("ingredient__name")
        shopping_list = create_shopping_cart_file(ingredients)
        response = HttpResponse(
            shopping_list, content_type="text/plain; charset=utf8"
        )
        response[
            "Content-Disposition"
        ] = "attachment; filename='shopping_cart.txt'"

        return response
