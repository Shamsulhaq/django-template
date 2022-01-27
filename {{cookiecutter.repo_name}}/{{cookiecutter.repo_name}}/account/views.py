from django.contrib.auth import logout
from django.shortcuts import render
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


from ..core.paginations import LimitPagination
from .filters import UserFilter
from .models import User
from .serializers import (
    ChangePasswordSerializer,
    EmailSerializer,
    OTPSerializer,
    ResendOtpSerializer,
    SignInSerializer,
    SignUpSerializer,
    UserSerializer,
)
from .utils import delete_user


class UserViewSet(ModelViewSet):
    filterset_class = UserFilter
    pagination_class = LimitPagination
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get_queryset(self):
        qs = User.objects.all()
        if self.request.user.is_admin:
            return qs
        else:
            qs = qs.filter(id=self.request.user.id)

    def destroy(self, request, *args, **kwargs):
        if request.user.is_admin:
            user = self.get_object()
            if not user.is_deleted:
                delete_user(user, request)
                user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            raise ValidationError(
                {
                    "deleted": "User already deleted"
                }
            )
        else:
            raise ValidationError(
                {
                    "permission-deny": "Permission required!"
                }
            )

    @action(url_path='me', detail=False, methods=['GET'])
    def me(self, request, **kwargs):
        user = request.user
        return Response(UserSerializer(user).data)

    @action(url_path='sign-up', detail=False, methods=['POST'], permission_classes=(permissions.AllowAny,))
    def sign_up(self, request, **kwargs):
        """Create New User"""
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        return Response(UserSerializer(obj).data, status=status.HTTP_201_CREATED)

    @action(url_path='sign-in', detail=False, methods=['POST'], permission_classes=(permissions.AllowAny,))
    def sign_in(self, request, **kwargs):
        """Login As user"""
        serializer = SignInSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        return Response(obj, status=status.HTTP_201_CREATED)

    @action(url_path='sign-out', detail=False, methods=['GET'], permission_classes=(permissions.IsAuthenticated,))
    def sign_out(self, request, **kwargs):
        """Logout with current session"""
        session_type = request.GET.get('session_type', 'app')
        if session_type in ['all', 'app']:
            try:
                Token.objects.get(user=request.user).delete()
            except Token.DoesNotExist:
                pass
        if session_type in ['all', 'web']:
            logout(request)
        return Response(
            {"message": "Successful"},
            status=status.HTTP_201_CREATED
        )

    @action(url_path="password-change", detail=False, methods=["PATCH"],
            permission_classes=(permissions.IsAuthenticated,))
    def password_change(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password change successful"}, status=status.HTTP_200_OK)

    @action(url_path='email-verify/(?P<token>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})',
            detail=False, methods=['GET'], permission_classes=(permissions.AllowAny,))
    def email_verify(self, request, token, **kwargs):
        try:
            user = User.objects.get(activation_token=token)
            user.activation_token = None
            user.is_email_verified = True
            user.save()
            message = "Your email has been successfully verified."
            return render(
                self.request,
                'email_verify.html',
                {
                    "title": "Success",
                    "message": message
                }
            )
        except User.DoesNotExist:
            message = "Expired Activation Token."
            return render(
                self.request,
                'email_verify.html',
                {
                    "title": "Expired",
                    "message": message
                }
            )

    @action(url_path='otp-verify', methods=['POST'], detail=False, permission_classes=(permissions.AllowAny,))
    def opt_verify(self, request, **kwargs):
        serializer = OTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message': 'Verified successful'})

    @action(url_path='add-phone', detail=False, methods=['PATCH'])
    def add_phone(self, request, **kwargs):
        phone = request.data.get('phone')
        user = request.user
        user.phone = phone
        user.is_phone_verified = False
        user.save()
        user.send_otp()
        return Response(UserSerializer(user).data)

    @action(url_path='resend-otp', methods=['POST'], detail=False, permission_classes=(permissions.AllowAny,))
    def resend_otp(self, request, **kwargs):
        serializer = ResendOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message': 'Send successful'})

    @action(url_path="resend-email-verification", detail=False, methods=["POST"],
            permission_classes=(permissions.AllowAny,))
    def resend_email_verification(self, request, *args, **kwargs):
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.perform_email_resend_activation(serializer.validated_data)
        return Response({"message": "Email activation mail send successful"}, status=status.HTTP_200_OK)

