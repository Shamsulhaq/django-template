# at spacium/accounts/utils.py
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.dispatch import receiver

# from django.urls import reverse
from django.utils import timezone
from django_rest_passwordreset.signals import reset_password_token_created
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from ..core.constants import HistoryActions
from .models import UnitOfHistory
from .serializers import UserSerializer
from .tasks import send_email_on_delay

User = get_user_model()


def get_deleted_email(email):
    if User.objects.filter(email__iexact=email).exists():
        return get_deleted_email(f'deleted-{email}')
    return email


def delete_user(user, request):
    deleted_by = request.user
    user.email = get_deleted_email(user.email)
    if user.phone:
        user.deleted_phone = user.phone
    user.phone = None
    user.is_deleted = True
    user.deleted_on = timezone.now()
    user.deleted_by = deleted_by
    user.is_active = False
    user.save()
    UnitOfHistory.user_history(
        action=HistoryActions.USER_DELETED,
        request=request,
        user=deleted_by,
        perform_for=user,
    )


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    """
    # reset_password_path = reverse('password_reset:reset-password-confirm')
    context = {
        'full_name': reset_password_token.user.name,
        'email': reset_password_token.user.email,
        # 'reset_password_url': f'{settings.SITE_URL}{reset_password_path}?token={reset_password_token.key}',
        'reset_password_url': f'{settings.WEBSITE_URL}/reset-password?token={reset_password_token.key}',
    }
    print(context['reset_password_url'], flush=True)
    template = 'emails/password_rest_mail.html'
    subject = 'Password Reset'
    send_email_on_delay.delay(template, context, subject, reset_password_token.user.email)
