from django.db import models


class StateChoices(models.TextChoices):
    Abu_Dhabi = "abu-dhabi"
    Al_Ain = "al-ain"
    Ajman = "ajman"
    Dubai = "dubai"
    Fujairah = "fujairah"
    Sharjah = "sharjah"
    Umm_Al_Quwain = "umm-al-quwain"
    Ras_Al_Khaimah = "ras-al-khaimah"


class HistoryActions(models.TextChoices):
    USER_SIGN_IN = 'user-sign-in'
    SOCIAL_SIGN_IN = 'social-sign-in'
    SOCIAL_SING_UP = 'social-sign-up'
    USER_DELETED = 'user-deleted'
    ACCEPTED_TERMS_AND_CONDITIONS = 'accepted-terms-and-conditions'
    ACCEPTED_PRIVACY_POLICY = 'accepted-privacy-policy'
    USER_UPDATE = 'user-update'
    RESEND_ACTIVATION = 'resend-email-activation'
    DOCUMENT_UPLOADED = 'document-uploaded'
    PROFILE_PICTURE_UPLOAD = 'profile-picture-upload'
    PASSWORD_CHANGE = 'password-change'
    PASSWORD_RESET_REQUEST = 'password-reset-request'
    PASSWORD_RESET = 'password-reset'
    ACCOUNT_DEACTIVATE = 'account-deactivate'
    ACCOUNT_REACTIVATE = 'account-reactivate'
    USER_BLOCKED = 'user-access-blocked'
    USER_UNBLOCKED = 'user-access-unblocked'
    PROFILE_PICTURE_VERIFIED = 'profile-picture-verified'
    PROFILE_PICTURE_REJECTED = 'profile-picture-rejected'
    DOCUMENT_VERIFIED = 'document-verified'
    DOCUMENT_REJECTED = 'document-rejected'
    AGREEMENT_UPDATED = 'agreement-updated'
    ADDED_VEHICLE = 'added-vehicle'
    UPDATE_VEHICLE = 'updated-vehicle'
    REMOVE_VEHICLE = 'removed-vehicle'
    REGISTER_SERVICE_PROVIDER = 'register-service-provider'
    UPDATE_PROVIDER_PROFILE = 'update-provicer-profile'
    ADD_SERVICE_AREA = 'add-service-area'
