from datetime import datetime, timezone
from flask import abort
from http import HTTPStatus

from .forms import (
    LoginForm,
    RegisterForm,
    ForgotPasswordForm,
    ResetPasswordForm,
    ChangePasswordForm,
    SendConfirmationForm,
)
from .models import AnonymousUser


class Config:
    SECRET_KEY = 'change_me_not_secret_key'

    SECURITY_TOKEN_AUTHENTICATION_KEY = 'auth_token'
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authentication-Token'
    SECURITY_TOKEN_MAX_AGE = None

    SECURITY_ANONYMOUS_USER = AnonymousUser
    SECURITY_UNAUTHORIZED_CALLBACK = lambda: abort(HTTPStatus.UNAUTHORIZED)

    # make datetimes timezone-aware by default
    SECURITY_DATETIME_FACTORY = lambda: datetime.now(timezone.utc)

    SECURITY_PASSWORD_SALT = 'security-password-salt'
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

    # login / logout
    # ==============
    SECURITY_LOGIN_FORM = LoginForm
    SECURITY_DEFAULT_REMEMBER_ME = False
    SECURITY_USER_IDENTITY_ATTRIBUTES = ['email']  # FIXME-identity
    SECURITY_POST_LOGIN_REDIRECT_ENDPOINT = '/'
    SECURITY_POST_LOGOUT_REDIRECT_ENDPOINT = '/'

    # registration
    # ============
    SECURITY_REGISTERABLE = False
    SECURITY_REGISTER_FORM = RegisterForm
    SECURITY_POST_REGISTER_REDIRECT_ENDPOINT = None
    SECURITY_SEND_REGISTER_EMAIL = True

    # email confirmation required functionality
    # =========================================
    SECURITY_CONFIRMABLE = False
    """Enable required email confirmation for new users."""

    SECURITY_SEND_CONFIRMATION_FORM = SendConfirmationForm
    """Form class to use for the re-send confirmation email form."""

    SECURITY_LOGIN_WITHOUT_CONFIRMATION = False
    """Allow users to login without confirming their email first."""

    SECURITY_CONFIRM_EMAIL_WITHIN = '5 days'
    """
    How long to wait until considering the token in confirmation emails to be expired.
    """

    SECURITY_POST_CONFIRM_REDIRECT_ENDPOINT = None
    SECURITY_CONFIRM_ERROR_REDIRECT_ENDPOINT = None

    # change password functionality
    # =============================
    SECURITY_CHANGEABLE = False
    SECURITY_CHANGE_PASSWORD_FORM = ChangePasswordForm
    SECURITY_POST_CHANGE_REDIRECT_ENDPOINT = None
    SECURITY_SEND_PASSWORD_CHANGED_EMAIL = True

    # forgot password functionality
    # =============================
    SECURITY_RECOVERABLE = False
    SECURITY_FORGOT_PASSWORD_FORM = ForgotPasswordForm

    # reset password
    # --------------
    SECURITY_RESET_PASSWORD_FORM = ResetPasswordForm
    SECURITY_RESET_PASSWORD_WITHIN = '5 days'
    SECURITY_POST_RESET_REDIRECT_ENDPOINT = None
    SECURITY_INVALID_RESET_TOKEN_REDIRECT = 'security_controller.forgot_password'
    SECURITY_EXPIRED_RESET_TOKEN_REDIRECT = 'security_controller.forgot_password'
    SECURITY_API_RESET_PASSWORD_HTTP_GET_REDIRECT = None
    SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL = True

    # trackable: record login stats, IPs, etc
    SECURITY_TRACKABLE = False


class TestConfig:
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECURITY_PASSWORD_HASH = 'plaintext'
