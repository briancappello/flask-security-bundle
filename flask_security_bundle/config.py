from datetime import datetime, timezone
from flask_security import AnonymousUser

from .forms import (
    LoginForm,
    ConfirmRegisterForm,
    RegisterForm,
    ForgotPasswordForm,
    ResetPasswordForm,
    ChangePasswordForm,
    SendConfirmationForm,
    PasswordlessLoginForm,
)


class BaseConfig:
    # NOTE: itsdangerous "salts" are not normal salts in the cryptographic
    # sense, see https://pythonhosted.org/itsdangerous/#the-salt
    SECURITY_PASSWORD_SALT = 'the-security-password-salt'

    SECURITY_LOGIN_FORM = LoginForm
    SECURITY_CONFIRM_REGISTER_FORM = ConfirmRegisterForm
    SECURITY_REGISTER_FORM = RegisterForm
    SECURITY_FORGOT_PASSWORD_FORM = ForgotPasswordForm
    SECURITY_RESET_PASSWORD_FORM = ResetPasswordForm
    SECURITY_CHANGE_PASSWORD_FORM = ChangePasswordForm
    SECURITY_SEND_CONFIRMATION_FORM = SendConfirmationForm
    SECURITY_PASSWORDLESS_LOGIN_FORM = PasswordlessLoginForm
    SECURITY_ANONYMOUS_USER = AnonymousUser

    # make datetimes timezone-aware by default
    SECURITY_DATETIME_FACTORY = lambda: datetime.now(timezone.utc)

    # disable flask-security's use of .txt templates (instead we
    # generate the plain text from the html message)
    SECURITY_EMAIL_PLAINTEXT = False

    # do not have the security extension register cli commands
    SECURITY_CLI_USERS_NAME = None
    SECURITY_CLI_ROLES_NAME = None

    SECURITY_RESET_PASSWORD_ENDPOINT = 'security.reset_password'
    SECURITY_API_RESET_PASSWORD_HTTP_GET_REDIRECT = 'security.reset_password'
    SECURITY_INVALID_RESET_TOKEN_REDIRECT = 'security.forgot_password'
    SECURITY_EXPIRED_RESET_TOKEN_REDIRECT = 'security.forgot_password'


class TestConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECURITY_PASSWORD_HASH_OPTIONS = dict(bcrypt={'rounds': 4})

    SECURITY_REGISTERABLE = True
    SECURITY_CONFIRMABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_CHANGEABLE = True
