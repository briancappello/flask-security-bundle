from flask import current_app as app
from flask_controller_bundle import url_for
from flask_security.confirmable import (
    generate_confirmation_token as security_generate_confirmation_token,
)
from flask_security.recoverable import (
    generate_reset_password_token as security_generate_reset_password_token,
    reset_password_token_status as security_reset_password_token_status,
)
from flask_security.signals import (
    confirm_instructions_sent,
    password_changed,
    password_reset,
    reset_password_instructions_sent,
    user_confirmed,
    user_registered,
)
from flask_security.utils import (
    get_message as security_get_message,
    login_user as security_login_user,
    logout_user as security_logout_user,
    send_mail as security_send_mail,
)
from flask_unchained import BaseService, injectable

from .user_manager import UserManager
from ..extensions import Security


class SecurityService(BaseService):
    def __init__(self,
                 security: Security = injectable,
                 user_manager: UserManager = injectable):
        self.security = security
        self.user_manager = user_manager

    def login_user(self, user, remember=None):
        """
        sends signal identity_changed (from flask_principal)

        Returns True if the user was successfully logged in, False otherwise
        """
        return security_login_user(user, remember)

    def process_login_errors(self, form):
        """
        try not to leak excess account info without being too unfriendly to
        actually-valid-users
        """
        account_disabled = security_get_message('DISABLED_ACCOUNT')[0]
        confirmation_required = security_get_message('CONFIRMATION_REQUIRED')[0]
        if account_disabled in form.errors.get('email', []):
            error = account_disabled
        elif confirmation_required in form.errors.get('email', []):
            error = confirmation_required
        else:
            identity_attrs = app.config.get('SECURITY_USER_IDENTITY_ATTRIBUTES')
            error = f"Invalid {', '.join(identity_attrs)} and/or password."
        form._errors = {'_error': [error]}
        return form

    def logout_user(self):
        """
        Logs out the current user and cleans up the remember me cookie (if any)

        sends signal identity_changed (from flask_principal)
        sends signal user_logged_out (from flask_login)
        """
        return security_logout_user()

    def register_user(self, user):
        """
        Performs the user registration process.

        sends signal user_registered

        Returns True if the user has been logged in, False otherwise.
        """
        should_login_user = (not self.security.confirmable
                             or self.security.login_without_confirmation)
        if should_login_user:
            user.active = True

        # confirmation token depends on having user.id set, which requires
        # the user be committed to the database
        self.user_manager.save(user, commit=True)

        confirmation_link, token = None, None
        if self.security.confirmable:
            token = security_generate_confirmation_token(user)
            confirmation_link = url_for('security.confirm_email',
                                        token=token, _external=True)

        user_registered.send(app._get_current_object(),
                             user=user, confirm_token=token)

        if app.config.get('SECURITY_SEND_REGISTER_EMAIL'):
            # FIXME-mail
            security_send_mail(
                subject=app.config.get('SECURITY_EMAIL_SUBJECT_REGISTER'),
                recipient=user.email,
                template='welcome',
                user=user,
                confirmation_link=confirmation_link)

        if should_login_user:
            return self.login_user(user)
        return False

    def change_password(self, user, password):
        user.password = password
        self.user_manager.save(user)
        self.send_password_changed_notice(user)
        password_changed.send(app._get_current_object(), user=user)

    def reset_password(self, user, password):
        user.password = password
        self.user_manager.save(user)
        self.send_password_reset_notice(user)
        password_reset.send(app._get_current_object(), user=user)

    def reset_password_token_status(self, token):
        return security_reset_password_token_status(token)

    def send_confirmation_instructions(self, user):
        """
        Sends the confirmation instructions email for the specified user.

        sends signal confirm_instructions_sent

        :param user: The user to send the instructions to
        """
        token = security_generate_confirmation_token(user)
        confirmation_link = url_for('security.confirm_email',
                                    token=token, _external=True)

        # FIXME-mail
        security_send_mail(app.config.get('SECURITY_EMAIL_SUBJECT_CONFIRM'),
                           user.email, 'confirmation_instructions', user=user,
                           confirmation_link=confirmation_link)

        confirm_instructions_sent.send(app._get_current_object(), user=user,
                                       token=token)

    def send_password_changed_notice(self, user):
        """
        Sends the password changed notice email for the specified user.

        :param user: The user to send the notice to
        """
        if app.config.get('SECURITY_SEND_PASSWORD_CHANGE_EMAIL'):
            # FIXME-mail
            security_send_mail(
                app.config.get('SECURITY_EMAIL_SUBJECT_PASSWORD_CHANGE_NOTICE'),
                user.email, 'change_notice', user=user)

    def send_password_reset_notice(self, user):
        """
        Sends the password reset notice email for the specified user.

        :param user: The user to send the notice to
        """
        if app.config.get('SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL'):
            # FIXME-mail
            security_send_mail(
                app.config.get('SECURITY_EMAIL_SUBJECT_PASSWORD_NOTICE'),
                user.email, 'reset_notice', user=user)

    def send_reset_password_instructions(self, user):
        """
        Sends the reset password instructions email for the specified user.

        :param user: The user to send the instructions to
        """
        token = security_generate_reset_password_token(user)
        reset_link = url_for('SECURITY_RESET_PASSWORD_ENDPOINT',
                             token=token, _external=True)

        if app.config.get('SECURITY_SEND_PASSWORD_RESET_EMAIL'):
            # FIXME-mail
            security_send_mail(
                subject=app.config.get('SECURITY_EMAIL_SUBJECT_PASSWORD_RESET'),
                recipient=user.email,
                template='reset_instructions', user=user, reset_link=reset_link)

        reset_password_instructions_sent.send(app._get_current_object(),
                                              user=user, token=token)

    def confirm_user(self, user):
        """Confirms the specified user"""
        if user.confirmed_at is not None:
            return False
        user.confirmed_at = self.security.datetime_factory()
        user.active = True
        self.user_manager.save(user)
        user_confirmed.send(app._get_current_object(), user=user)
        return True
