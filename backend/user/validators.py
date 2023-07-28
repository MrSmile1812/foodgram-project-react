from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class UnicodeUsernameValidator(validators.RegexValidator):
    regex = r"^[\w.@+-]+\Z"
    message = _(
        "Введите корректный никнейм. Это значение может содержать только, "
        "буквы, цифры и символы - @/./+/-/_ ."
    )
    flags = 0
