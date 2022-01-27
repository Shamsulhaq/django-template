# at ./backend/user/models.py
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .tasks import send_otp_on_delay, send_email_on_delay
from .choices import GenderChoices, DeviceTypeChoices
from .managers import UserManager, UserDeviceTokenManager
from ..core.utils import create_token, build_absolute_uri, create_otp
from ..core.validators import username_validator
from ..core.models import BaseModel


class User(AbstractBaseUser, PermissionsMixin):
    """Store custom user information.
    all fields are common for all users."""
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    name = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )
    email = models.EmailField(
        max_length=100,
        unique=True
    )  # unique email to perform email login and send alert mail.
    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$",
        message="Enter Phone number with country code"
    )  # phone number validator.
    phone = models.CharField(
        _("phone number"),
        validators=[phone_regex],
        max_length=15,
        unique=True,
        blank=True,
        null=True
    )
    gender = models.CharField(
        max_length=8,
        choices=GenderChoices.choices,
        blank=True,
        null=True
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True
    )
    # Profile Picture
    photo = models.ImageField(
        'ProfilePicture',
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )
    # Verification Check
    activation_token = models.UUIDField(
        blank=True,
        null=True
    )
    activation_token_created = models.DateTimeField(
        blank=True,
        null=True
    )
    otp = models.CharField(
        max_length=6
    )
    otp_created = models.DateTimeField(
        blank=True,
        null=True
    )
    is_email_verified = models.BooleanField(
        default=False
    )
    is_phone_verified = models.BooleanField(
        default=False
    )
    term_and_condition_accepted = models.BooleanField(
        default=False
    )
    privacy_policy_accepted = models.BooleanField(
        default=False
    )
    # permission
    is_active = models.BooleanField(
        default=True
    )
    is_staff = models.BooleanField(
        default=False
    )
    is_superuser = models.BooleanField(
        default=False
    )  # main man of this application.
    is_deleted = models.BooleanField(
        default=False
    )
    deleted_on = models.DateTimeField(
        null=True,
        blank=True
    )
    deleted_phone = models.CharField(
        max_length=15,
        unique=True,
        blank=True,
        null=True
    )

    # details
    last_active_on = models.DateTimeField(
        null=True,
        blank=True
    )
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now
    )
    deactivation_reason = models.TextField(
        null=True,
        blank=True
    )
    # last login will provide by django abstract_base_user.
    # password also provide by django abstract_base_user.
    USERNAME_FIELD = 'username'
    objects = UserManager()

    def __str__(self) -> str:
        return self.username

    @property
    def is_admin(self):
        return self.is_staff or self.is_superuser

    def send_email_verification(self):
        self.activation_token = create_token()
        self.is_email_verified = False
        self.activation_token_created = timezone.now()
        self.save()
        context = {
            'full_name': self.name,
            'email': self.email,
            'url': build_absolute_uri(f"api/v1/users/email-verify/{self.activation_token}/"),
        }
        template = 'emails/sing_up_email.html'
        subject = 'Email Verification'
        # send_email_on_delay.delay(template, context, subject, self.email)

    def send_otp(self):
        self.otp = create_otp()
        self.is_phone_verified = False
        self.otp_created = timezone.now()
        self.save()
        # send_otp_on_delay.delay(self.phone, self.otp)


class UnitOfHistory(models.Model):
    """We will create log for every action
    those data will store in this model"""

    action = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )  # in this field we will define which action was perform.
    created = models.DateTimeField(
        auto_now_add=True
    )
    old_meta = models.JSONField(
        null=True
    )  # we store data what was the scenario before perform this action.
    new_meta = models.JSONField(
        null=True
    )  # we store data after perform this action.
    header = models.JSONField(
        null=True
    )  # request header that will provide user browser
    # information and others details.
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="performer"
    )  # this user will be action performer.
    perform_for = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="perform_for"
    )  # sometime admin/superior  will perform some
    # specific action for employee/or user e.g. payroll change.
    # Generic Foreignkey Configuration. DO NOT CHANGE
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.CharField(
        max_length=100
    )
    content_object = GenericForeignKey()

    def __str__(self) -> str:
        return self.action or "action"

    @classmethod
    def user_history(
        cls,
        action,
        user,
        request,
        new_meta=None,
        old_meta=None,
        perform_for=None
    ) -> object:
        try:
            data = {i[0]: i[1] for i in request.META.items() if i[0].startswith('HTTP_')}
        except BaseException:
            data = None
        cls.objects.create(
            action=action,
            user=user,
            old_meta=old_meta,
            new_meta=new_meta,
            header=data,
            perform_for=perform_for,
            content_type=ContentType.objects.get_for_model(User),
            object_id=user.id
        )


class UserDeviceToken(BaseModel):
    """
    To Trigier FMC notification we need
    device token will store user device token
    to trigier notification.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    device_token = models.CharField(
        max_length=200
    )
    device_type = models.CharField(
        max_length=8,
        choices=DeviceTypeChoices.choices
    )
    objects = UserDeviceTokenManager()

    def __str__(self):
        return self.user
