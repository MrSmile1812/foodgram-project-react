from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from django.db.models import Sum
from django.shortcuts import get_object_or_404

from recipes.models import (
    Favorite,
    Ingredients,
    IngredientsInRecipes,
    Recipes,
    ShoppingCart,
    Tags,
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
from .utils import shopping_cart_file


class TagsViewSet(viewsets.ModelViewSet):
    """Класс для работы с моделью Tags."""

    queryset = Tags.objects.all()
    serializer_class = TagsSerializer


class IngredientsViewSet(viewsets.ModelViewSet):
    """Класс для работы с Ingredients."""

    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    filter_backends = [IngredientFilter]
    search_fields = ("^name",)


class UsersViewSet(UserViewSet):
    """Класс для работы с User."""

    queryset = User.objects.all()
    serializer_class = UserSerializer

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
        queryset = Follow.objects.filter(user=user)
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
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == "POST":
            serializer = FollowSerializer(
                Follow.objects.create(user=user, author=author),
                context={"request": request},
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        Follow.objects.filter(user=user, author=author).delete()
        return Response("Успешная отписка", status=status.HTTP_204_NO_CONTENT)


class RecipesViewSet(viewsets.ModelViewSet):
    """Класс для работы с моделью Recipes."""

    queryset = Recipes.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_class = (AuthorOrReadOnly,)
    pagination_class = CustomPaginator

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipesReadSerializer
        return RecipesWriteSerializer

    def post_delete_recipe(self, request, pk, model):
        recipe = get_object_or_404(Recipes, pk=pk)
        user = self.request.user
        if request.method == "POST":
            serializer = ShoppingListFavoiriteSerializer(recipe)
            if model.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {"errors": "Рецепт уже добавлен!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            model.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            if model.objects.filter(user=user, recipe=recipe).exists():
                model.objects.get(user=user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {"errors": "Рецепт уже удален!"},
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
    )
    def shopping_cart(self, request, **kwargs):
        return self.post_delete_recipe(request, kwargs.pop("pk"), ShoppingCart)

    @action(methods=["GET"], detail=False, permission_class=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = IngredientsInRecipes.objects.select_related(
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
        return shopping_cart_file(ingredients)
