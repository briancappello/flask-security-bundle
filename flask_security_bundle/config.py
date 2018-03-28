from datetime import datetime, timezone
from flask import abort, current_app
from flask_security import AnonymousUser
from http import HTTPStatus
from werkzeug.local import LocalProxy

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
    SECURITY_CONFIRMABLE = False
    SECURITY_REGISTERABLE = False
    SECURITY_RECOVERABLE = False
    SECURITY_TRACKABLE = False
    SECURITY_PASSWORDLESS = False
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
    SECURITY_PASSWORDLESS_LOGIN_FORM = PasswordlessLoginForm
    SECURITY_ANONYMOUS_USER = AnonymousUser

    # FIXME these are named rather confusingly
    SECURITY_POST_LOGIN_VIEW = '/'
    SECURITY_POST_LOGOUT_VIEW = '/'
    SECURITY_CONFIRM_ERROR_VIEW = None
    SECURITY_POST_REGISTER_VIEW = None
    SECURITY_POST_CONFIRM_VIEW = None
    SECURITY_POST_RESET_VIEW = None
    SECURITY_POST_CHANGE_VIEW = None

    SECURITY_RESET_PASSWORD_ENDPOINT = 'security.reset_password'
    SECURITY_API_RESET_PASSWORD_HTTP_GET_REDIRECT = 'security.reset_password'
    SECURITY_INVALID_RESET_TOKEN_REDIRECT = 'security.forgot_password'
    SECURITY_EXPIRED_RESET_TOKEN_REDIRECT = 'security.forgot_password'

    SECURITY_SEND_REGISTER_EMAIL = True
    SECURITY_SEND_PASSWORD_CHANGE_EMAIL = True
    SECURITY_SEND_PASSWORD_RESET_EMAIL = True
    SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL = True

    # FIXME-mail
    SECURITY_EMAIL_SUBJECT_REGISTER = 'Welcome'
    SECURITY_EMAIL_SUBJECT_CONFIRM = 'Please confirm your email'
    SECURITY_EMAIL_SUBJECT_PASSWORDLESS = 'Login instructions'
    SECURITY_EMAIL_SUBJECT_PASSWORD_NOTICE = 'Your password has been reset'
    SECURITY_EMAIL_SUBJECT_PASSWORD_CHANGE_NOTICE = \
        'Your password has been changed'
    SECURITY_EMAIL_SUBJECT_PASSWORD_RESET = 'Password reset instructions'
    SECURITY_EMAIL_SENDER = LocalProxy(lambda: current_app.config.get(
        'MAIL_DEFAULT_SENDER', 'no-reply@localhost'))

    SECURITY_EMAIL_HTML = True
    # disable flask-security's use of .txt templates (instead we
    # generate the plain text from the html message)
    SECURITY_EMAIL_PLAINTEXT = False

    # make datetimes timezone-aware by default
    SECURITY_DATETIME_FACTORY = lambda: datetime.now(timezone.utc)

    # FIXME-i18n
    SECURITY_I18N_DOMAIN = 'flask_security'

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


class TestConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECURITY_PASSWORD_HASH_OPTIONS = dict(bcrypt={'rounds': 4})
