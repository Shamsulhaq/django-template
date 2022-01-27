# at matrimony/backend/users/choices.py
from django.db import models


class GenderChoices(models.TextChoices):
    Female = "female"
    Male = "male"


class DeviceTypeChoices(models.TextChoices):
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"