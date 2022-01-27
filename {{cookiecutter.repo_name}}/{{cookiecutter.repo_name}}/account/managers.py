# at matrimony/backend/user/managers.py
from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(
        self,
        username,
        password,
        is_staff,
        is_superuser,
        **extra_fields
    ) -> object:
        """
        Create User With Email name password
        """
        if not username:
            raise ValueError("User must have an Username")
        user = self.model(
            username=username,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(
            self,
            username,
            password
    ) -> object:
        return self.create_user(username, password, True, True)


class UserDeviceTokenManager(BaseUserManager):

    def create_or_update(self, user, device_type, device_token):
        try:
            raw = self.get(user=user)
            raw.device_token = device_token
            raw.device_type = device_type
            raw.save()
            return raw
        except self.model.DoesNotExist:
            return self.create(
                user=user,
                device_type=device_type,
                device_token=device_token
            )

