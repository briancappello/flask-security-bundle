from datetime import datetime, timezone
from flask import abort, current_app
from http import HTTPStatus
from werkzeug.local import LocalProxy

from .forms import (
    LoginForm,
    RegisterForm,
    ForgotPasswordForm,
    ResetPasswordForm,
    ChangePasswordForm,
    SendConfirmationForm,
)
from .models import AnonymousUser


def _should_send_mail(config_option, default=None):
    def get_value():
        if 'mail_bundle' not in current_app.unchained.bundles:
            return False
        value = current_app.config.get(config_option, None)
        if value is not None:
            return value
        return default
    return LocalProxy(lambda: get_value())


class Config:
    """
    Default configuration settings for the Security Bundle.
    """

    SECURITY_TOKEN_AUTHENTICATION_KEY = 'auth_token'
    """
    Specifies the query string parameter to read when using token authentication.
    """

    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authentication-Token'
    """
    Specifies the HTTP header to read when using token authentication.
    """

    SECURITY_TOKEN_MAX_AGE = None
    """
    Specifies the number of seconds before an authentication token expires.
    Defaults to None, meaning the token never expires.
    """

    SECURITY_ANONYMOUS_USER = AnonymousUser
    """
    Class to use for representing anonymous users.
    """

    SECURITY_UNAUTHORIZED_CALLBACK = lambda: abort(HTTPStatus.UNAUTHORIZED)
    """
    This callback gets called when authorization fails. By default we abort with
    an HTTP status code of 401 (UNAUTHORIZED).
    """

    # make datetimes timezone-aware by default
    SECURITY_DATETIME_FACTORY = lambda: datetime.now(timezone.utc)
    """
    Factory function to use when creating new dates. By default we use
    :python:`datetime.now(timezone.utc)` to create a timezone-aware datetime.
    """

    SECURITY_PASSWORD_SALT = 'security-password-salt'
    """
    Specifies the HMAC salt. This is only used if the password hash type is
    set to something other than plain text.
    """

    SECURITY_PASSWORD_HASH = 'bcrypt'
    """
    Specifies the password hash algorithm to use when hashing passwords.
    Recommended values for production systems are argon2, bcrypt, or pbkdf2_sha512.
    """

    SECURITY_PASSWORD_SINGLE_HASH = False
    """
    Specifies that passwords should only be hashed once. By default, passwords
    are hashed twice, first with SECURITY_PASSWORD_SALT, and then with a random
    salt. May be useful for integrating with other applications.
    """

    SECURITY_PASSWORD_SCHEMES = ['argon2',
                                 'bcrypt',
                                 'pbkdf2_sha512',
                                 # and always the last one...
                                 'plaintext']
    """
    List of algorithms that can be used for hashing passwords.
    """

    SECURITY_PASSWORD_HASH_OPTIONS = {}
    """
    Specifies additional options to be passed to the hashing method.
    """

    SECURITY_DEPRECATED_PASSWORD_SCHEMES = ['auto']
    """
    List of deprecated algorithms for hashing passwords.
    """

    SECURITY_HASHING_SCHEMES = ['sha512_crypt']
    """
    List of algorithms that can be used for creating and validating tokens.
    """

    SECURITY_DEPRECATED_HASHING_SCHEMES = []
    """
    List of deprecated algorithms for creating and validating tokens.
    """

    # login / logout
    # ==============
    SECURITY_LOGIN_FORM = LoginForm
    """
    The form class to use for the login view.
    """

    SECURITY_DEFAULT_REMEMBER_ME = False
    """
    Whether or not the login form should default to checking the
    "Remember me?" option.
    """

    SECURITY_USER_IDENTITY_ATTRIBUTES = ['email']  # FIXME-identity
    """
    List of attributes on the user model that can used for logging in with.
    Each must be unique.
    """

    SECURITY_POST_LOGIN_REDIRECT_ENDPOINT = '/'
    """
    The endpoint or url to redirect to after a successful login.
    """

    SECURITY_POST_LOGOUT_REDIRECT_ENDPOINT = '/'
    """
    The endpoint or url to redirect to after a user logs out.
    """

    # registration
    # ============
    SECURITY_REGISTERABLE = False
    """
    Whether or not to enable registration.
    """

    SECURITY_REGISTER_FORM = RegisterForm
    """
    The form class to use for the register view.
    """

    SECURITY_POST_REGISTER_REDIRECT_ENDPOINT = None
    """
    The endpoint or url to redirect to after a user completes the
    registration form.
    """

    SECURITY_SEND_REGISTER_EMAIL = _should_send_mail(
        'SECURITY_SEND_REGISTER_EMAIL', True)
    """
    Whether or not send a welcome email after a user completes the
    registration form.
    """

    # email confirmation required functionality
    # =========================================
    SECURITY_CONFIRMABLE = False
    """
    Whether or not to enable required email confirmation for new users.
    """

    SECURITY_SEND_CONFIRMATION_FORM = SendConfirmationForm
    """
    Form class to use for the (re)send confirmation email form.
    """

    SECURITY_LOGIN_WITHOUT_CONFIRMATION = False
    """
    Allow users to login without confirming their email first. (This option
    only applies when :attr:`SECURITY_CONFIRMABLE` is True.)
    """

    SECURITY_CONFIRM_EMAIL_WITHIN = '5 days'
    """
    How long to wait until considering the token in confirmation emails to
    be expired.
    """

    SECURITY_POST_CONFIRM_REDIRECT_ENDPOINT = None
    """
    Endpoint or url to redirect to after the user confirms their email.
    Defaults to :attr:`SECURITY_POST_LOGIN_REDIRECT_ENDPOINT`.
    """

    SECURITY_CONFIRM_ERROR_REDIRECT_ENDPOINT = None
    """
    Endpoint to redirect to if there's an error confirming the user's email.
    """

    # change password functionality
    # =============================
    SECURITY_CHANGEABLE = False
    """
    Whether or not to enable change password functionality.
    """

    SECURITY_CHANGE_PASSWORD_FORM = ChangePasswordForm
    """
    Form class to use for the change password view.
    """

    SECURITY_POST_CHANGE_REDIRECT_ENDPOINT = None
    """
    Endpoint or url to redirect to after the user changes their password.
    """

    SECURITY_SEND_PASSWORD_CHANGED_EMAIL = _should_send_mail(
        'SECURITY_SEND_PASSWORD_CHANGED_EMAIL', True)
    """
    Whether or not to send the user an email when their password has been changed.
    Defaults to True, and it's strongly recommended to leave this option enabled.
    """

    # forgot password functionality
    # =============================
    SECURITY_RECOVERABLE = False
    """
    Whether or not to enable forgot password functionality.
    """

    SECURITY_FORGOT_PASSWORD_FORM = ForgotPasswordForm
    """
    Form class to use for the forgot password form.
    """

    # reset password
    # --------------
    SECURITY_RESET_PASSWORD_FORM = ResetPasswordForm
    """
    Form class to use for the reset password form.
    """

    SECURITY_RESET_PASSWORD_WITHIN = '5 days'
    """
    Specifies the amount of time a user has before their password reset link
    expires. Always pluralized the time unit for this value. Defaults to 5 days.
    """

    SECURITY_POST_RESET_REDIRECT_ENDPOINT = None
    """
    Endpoint or url to redirect to after the user resets their password.
    """

    SECURITY_INVALID_RESET_TOKEN_REDIRECT = 'security_controller.forgot_password'
    """
    Endpoint or url to redirect to if the reset token is invalid.
    """

    SECURITY_EXPIRED_RESET_TOKEN_REDIRECT = 'security_controller.forgot_password'
    """
    Endpoint or url to redirect to if the reset token is expired.
    """

    SECURITY_API_RESET_PASSWORD_HTTP_GET_REDIRECT = None
    """
    Endpoint or url to redirect to if a GET request is made to the reset password
    view. Defaults to None, meaning no redirect. Useful for single page apps.
    """

    SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL = _should_send_mail(
        'SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL', True)
    """
    Whether or not to send the user an email when their password has been reset.
    Defaults to True, and it's strongly recommended to leave this option enabled.
    """


class TestConfig:
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECURITY_PASSWORD_HASH = 'plaintext'
