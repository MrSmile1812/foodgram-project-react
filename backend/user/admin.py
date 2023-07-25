from django.contrib import admin

from user.models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
    )
    search_fields = (
        "username",
        "email",
    )
    list_filter = (
        "first_name",
        "email",
    )
    list_display_links = ("username",)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("user", "author")
    list_filter = ("user", "author")
    search_fields = ("user", "author")
