from rest_framework import routers

from django.urls import include, path

from api.v1.views import (
    IngredientsViewSet,
    RecipesViewSet,
    TagsViewSet,
    UsersViewSet,
)


app_name = "api"

router = routers.DefaultRouter()

router.register(r"users", UsersViewSet, basename="users")
router.register(r"tags", TagsViewSet, basename="tags")
router.register(r"recipes", RecipesViewSet, basename="recipes")
router.register(r"ingredients", IngredientsViewSet, basename="ingredients")


urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
