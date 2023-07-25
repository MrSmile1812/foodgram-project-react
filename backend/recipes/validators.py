from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class SlugValidator(validators.RegexValidator):
    regex = r"^[-a-zA-Z0-9_]+$"
    message = _(
        "Enter a valid name. This value may contain only letters and numbers."
    )
    flags = 0
