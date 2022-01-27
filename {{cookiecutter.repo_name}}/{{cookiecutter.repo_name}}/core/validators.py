import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def username_validator(value):
    """
        The username consists of 6 to 30 characters inclusive.
        If the username consists of less than 6 or greater than 30 characters,
        then it is an invalid username.
        The username can only contain alphanumeric characters and underscores (_).
        Alphanumeric characters describe the character set consisting of lowercase characters [a – z],
        uppercase characters [A – Z], and digits [0 – 9].
        The first character of the username must be an alphabetic character,
        i.e., either lowercase character [a – z] or uppercase character [A – Z].
    """
    length = len(value)
    regex = r'^[a-zA-Z][a-zA-Z0-9_]+$'
    if not (re.search(regex, value)):
        raise ValidationError(_("username should be alphanumeric"))
    elif length < 6 or length > 30:
        raise ValidationError(_("username length should not less than 6 and greater than 30 characters."))
