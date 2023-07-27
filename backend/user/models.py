from django.contrib.auth.models import AbstractUser
from django.db import models

from user.validators import UnicodeUsernameValidator


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        verbose_name="Никнейм",
        max_length=150,
        unique=True,
        help_text=(
            "Обязательное поле. Максимум 150 символов."
            "Только буквы, цифры и @/./+/-/_."
        ),
        validators=[username_validator],
        error_messages={
            "unique": ("Пользователь с таким никнеймом уже существует."),
        },
    )
    email = models.EmailField(
        verbose_name="Email",
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name="Имя", blank=True, max_length=150
    )
    last_name = models.CharField(
        verbose_name="Фамилия", blank=True, max_length=150
    )

    password = models.CharField(
        "Пароль",
        max_length=150,
        blank=False,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
        "first_name",
        "last_name",
        "password",
    ]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-id"]

    def __str__(self):
        return self.email


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="Подписчик",
        related_name="follower",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="Автор",
        related_name="following",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ("user",)
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="uq_user_author"
            )
        ]
