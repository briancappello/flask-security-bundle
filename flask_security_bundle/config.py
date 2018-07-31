from datetime import datetime, timezone
from flask import abort
from flask_security import AnonymousUser
from http import HTTPStatus

from .forms import (
    LoginForm,
    ConfirmRegisterForm,
    RegisterForm,
    ForgotPasswordForm,
    ResetPasswordForm,
    ChangePasswordForm,
    SendConfirmationForm,
)


class Config:
    SECRET_KEY = 'change_me_not_secret_key'
    SECURITY_PASSWORD_SALT = 'security-password-salt'

    SECURITY_CONFIRMABLE = False
    SECURITY_REGISTERABLE = False
    SECURITY_RECOVERABLE = False
    SECURITY_TRACKABLE = False
    SECURITY_CHANGEABLE = False

    SECURITY_LOGIN_WITHIN = '1 days'
    SECURITY_LOGIN_WITHOUT_CONFIRMATION = False
    SECURITY_DEFAULT_REMEMBER_ME = False
    SECURITY_CONFIRM_EMAIL_WITHIN = '5 days'
    SECURITY_RESET_PASSWORD_WITHIN = '5 days'
    SECURITY_TOKEN_AUTHENTICATION_KEY = 'auth_token'
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authentication-Token'
    SECURITY_TOKEN_MAX_AGE = None
    SECURITY_UNAUTHORIZED_CALLBACK = lambda: abort(HTTPStatus.UNAUTHORIZED)

    # FIXME-identity
    SECURITY_USER_IDENTITY_ATTRIBUTES = ['email']

    SECURITY_LOGIN_FORM = LoginForm
    SECURITY_CONFIRM_REGISTER_FORM = ConfirmRegisterForm
    SECURITY_REGISTER_FORM = RegisterForm
    SECURITY_FORGOT_PASSWORD_FORM = ForgotPasswordForm
    SECURITY_RESET_PASSWORD_FORM = ResetPasswordForm
    SECURITY_CHANGE_PASSWORD_FORM = ChangePasswordForm
    SECURITY_SEND_CONFIRMATION_FORM = SendConfirmationForm
    SECURITY_ANONYMOUS_USER = AnonymousUser

    SECURITY_POST_LOGIN_REDIRECT_ENDPOINT = '/'
    SECURITY_POST_LOGOUT_REDIRECT_ENDPOINT = '/'
    SECURITY_CONFIRM_ERROR_REDIRECT_ENDPOINT = None
    SECURITY_POST_REGISTER_REDIRECT_ENDPOINT = None
    SECURITY_POST_CONFIRM_REDIRECT_ENDPOINT = None
    SECURITY_POST_RESET_REDIRECT_ENDPOINT = None
    SECURITY_POST_CHANGE_REDIRECT_ENDPOINT = None

    SECURITY_FORGOT_PASSWORD_ENDPOINT = 'security_controller.forgot_password'
    SECURITY_API_RESET_PASSWORD_HTTP_GET_REDIRECT = None
    SECURITY_INVALID_RESET_TOKEN_REDIRECT = 'security_controller.forgot_password'
    SECURITY_EXPIRED_RESET_TOKEN_REDIRECT = 'security_controller.forgot_password'

    SECURITY_SEND_REGISTER_EMAIL = True
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = True
    SECURITY_SEND_PASSWORD_RESET_EMAIL = True
    SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL = True

    # make datetimes timezone-aware by default
    SECURITY_DATETIME_FACTORY = lambda: datetime.now(timezone.utc)

    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_PASSWORD_SINGLE_HASH = False
    SECURITY_PASSWORD_SCHEMES = ['argon2',
                                 'bcrypt',
                                 'pbkdf2_sha512',
                                 # and always the last one...
                                 'plaintext']
    SECURITY_DEPRECATED_PASSWORD_SCHEMES = ['auto']
    SECURITY_HASHING_SCHEMES = ['sha512_crypt']
    SECURITY_DEPRECATED_HASHING_SCHEMES = []


class TestConfig:
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECURITY_PASSWORD_HASH = 'plaintext'
