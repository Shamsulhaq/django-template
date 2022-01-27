from django.contrib.auth import authenticate, login
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (
    BooleanField,
    CharField,
    EmailField,
    ModelSerializer,
    Serializer,
)

from ..core.constants import HistoryActions

from .models import (
    User,
    UnitOfHistory,
    UserDeviceToken,
)


class BioSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'name',
            'phone',
            'email',
            'gender',
            'last_active_on'
        )


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'name',
            'phone',
            'email',
            'gender',
            'is_deleted',
            'last_active_on',
            'date_joined',
            'is_phone_verified',
            'is_email_verified',
            'is_active',
            'is_staff',
            'is_admin'
        )
        read_only_fields = (
            'id',
            'is_active',
            'is_staff',
            'is_deleted',
            'last_active_on',
            'date_joined',
            'activation_token',
            'is_admin'
        )


class SignUpSerializer(ModelSerializer):
    referral = CharField(required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'phone',
            'name',
            'email',
            'username',
            'password',
            'gender',
        )

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data, *args, **kwargs):
        password = validated_data.pop("password", None)
        instance = super(SignUpSerializer, self).create(validated_data, *args, **kwargs)
        if password:
            instance.set_password(password)
            instance.term_and_condition_accepted = True
            instance.save()
            if instance.email:
                instance.send_email_verification()
            if instance.phone:
                instance.send_otp()
        return instance

    def update(self, instance, validated_data, *args, **kwargs):
        password = validated_data.pop("password", None)
        instance = super(SignUpSerializer, self).update(instance, validated_data, *args, **kwargs)
        if password:
            instance.set_password(password)
            instance.save()
        return instance


class SignInSerializer(Serializer):
    username = CharField(required=True, error_messages={'message': "username, email or phone is required to signup"})
    password = CharField(required=True, error_messages={'message': "password is required"})
    activate = BooleanField(required=False)

    def create(self, validated_data):
        username = validated_data.get('username')
        password = validated_data.get('password')
        activate = validated_data.get('activate')
        request = self.context['request']
        try:
            user = User.objects.get(
                Q(email=username)
                | Q(phone=username)
                | Q(username=username)
            )
        except User.DoesNotExist:
            raise ValidationError(
                {
                    "does-not-exist": "user is not exist with this email or phone"
                }
            )
        # if user.activation_token or not user.is_email_verified:
        #     raise ValidationError({
        #         "email-not-verified": "Please verify your email address."
        #     })
        # elif user.otp or not user.is_phone_verified:
        #     raise ValidationError({
        #         "phone-not-verified": "Please verify your phone number."
        #     })

        if not user.is_active and user.deactivation_reason:
            if activate:
                user.is_active = True
                user.deactivation_reason = None
                user.save()
            else:
                raise ValidationError({
                    "deactivated-account": "Account deactivated."
                })

        elif not user.is_active:
            raise ValidationError({
                "account-blocked": "Your account is temporary blocked. Please connect with support"
            })
        user = authenticate(username=user.email, password=password)
        if user is None:
            raise ValidationError(
                {
                    "wrong-credentials": "wrong credentials"
                }
            )
        login(request=request, user=user)
        UnitOfHistory.user_history(
            action=HistoryActions.USER_SIGN_IN,
            user=user,
            request=request
        )
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        data = UserSerializer(user).data
        data['token'] = token.key
        return data


class EmailSerializer(Serializer):
    email = EmailField()

    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        if not user:
            raise ValidationError("No user exists with given email.")
        return value

    def perform_email_resend_activation(self, validated_data, *args, **kwargs):
        email = validated_data.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError({"email": "No user exists with given email."})
        if user.activation_token is None:
            raise ValidationError({"email": "Email already verified."})
        user.send_email_verification()
        return user


class OTPSerializer(Serializer):
    phone = CharField(required=True)
    otp = CharField(required=True)

    def validate(self, data):
        phone = data['phone']
        user = User.objects.filter(phone=phone).first()
        if not user:
            raise ValidationError({'otp-verify': "Invalid OTP"})
        if user.otp == data['otp']:
            user.otp = None
            user.is_phone_verified = True
            user.save()
            return data
        raise ValidationError({'otp-verify': "Invalid OTP"})


class ResendOtpSerializer(Serializer):
    phone = CharField(required=True)

    def validate(self, data):
        phone = data['phone']
        user = User.objects.filter(phone=phone).first()
        if not user:
            raise ValidationError({'otp-resend': "User not found with this phone"})
        user.send_otp()
        return data


class ChangePasswordSerializer(Serializer):
    old_password = CharField(required=True)
    new_password = CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data, *args, **kwargs):
        user = self.context['request'].user
        old_password = validated_data.get("old_password")
        if not user.check_password(old_password):
            raise ValidationError({"password-change": "Wrong password."})

        user.set_password(validated_data.get("new_password"))
        user.save()
        UnitOfHistory.user_history(
            action=HistoryActions.PASSWORD_CHANGE,
            user=user,
            request=self.context['request']
        )
        return user


class UserDevicesTokenSerializer(ModelSerializer):
    class Meta:
        model = UserDeviceToken
        fields = ['device_token', 'device_type', 'user']
        read_only_fields = ['user']

    def create(self, validated_data, *args, **kwargs):
        device_type = validated_data.get('device_type')
        device_token = validated_data.get('device_token')
        user = self.context['request'].user
        if device_type and device_token:
            user_token = UserDeviceToken.objects.filter(user=user).first()
            if not user_token:
                user_token = UserDeviceToken(user=user)

            user_token.device_type = device_type
            user_token.device_token = device_token
            user_token.save()
            obj = UserDeviceToken.objects.filter(
                device_type=device_type,
                device_token=device_token
            ).exclude(
                user=user
            ).delete()
            return obj