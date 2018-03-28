from datetime import datetime, timezone
from flask import current_app as app, session
from flask_controller_bundle import get_url
from flask_login import logout_user
from flask_principal import AnonymousIdentity, identity_changed
from flask_security import current_user
from flask_security.changeable import (
    send_password_changed_notice as security_send_password_changed_notice,
)
from flask_security.confirmable import (
    send_confirmation_instructions as security_send_confirmation_instructions,
    generate_confirmation_link as security_generate_confirmation_link,
    confirm_email_token_status as security_confirm_email_token_status,
)
from flask_security.recoverable import (
    send_password_reset_notice as security_send_password_reset_notice,
    generate_reset_password_token as security_generate_reset_password_token,
    reset_password_token_status as security_reset_password_token_status,
)
from flask_security.signals import (
    password_changed,
    password_reset,
    reset_password_instructions_sent,
    user_confirmed,
    user_registered,
)
from flask_security.utils import (
    get_message as security_get_message,
    login_user as security_login_user,
    send_mail as security_send_mail,
)
from flask_security.views import _security as security
from flask_sqlalchemy_bundle import SessionManager
from flask_unchained import BaseService, injectable


class SecurityService(BaseService):
    def __init__(self, session_manager: SessionManager = injectable):
        self.session_manager = session_manager

    def login_user(self, user, remember=None):
        """
        sends signal identity_changed

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
        logout the current user (if any)

        sends signal identity_changed (from flask_principal)
        sends signal user_logged_out (from flask_login)
        """
        for key in ('identity.name', 'identity.auth_type'):
            session.pop(key, None)
        identity_changed.send(app._get_current_object(),
                              identity=AnonymousIdentity())
        return logout_user()

    def register_user(self, user):
        """
        Performs the user registration process.

        sends signal user_registered

        Returns True if the user has been logged in, False otherwise.
        """
        if not security.confirmable or security.login_without_confirmation:
            user.active = True

        # confirmation token depends on having user.id set, which requires
        # the user be committed to the database
        self.session_manager.add(user, commit=True)

        confirmation_link, token = None, None
        if security.confirmable:
            confirmation_link, token = security_generate_confirmation_link(user)

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

        if not security.confirmable or security.login_without_confirmation:
            return self.login_user(user)
        return False

    def change_password(self, user, password):
        user.password = password
        self.session_manager.add(user, commit=True)
        self.send_password_changed_notice(user)
        password_changed.send(app._get_current_object(), user=user)

    def reset_password(self, user, password):
        user.password = password
        self.session_manager.add(user, commit=True)
        self.send_password_reset_notice(user)
        password_reset.send(app._get_current_object(), user=user)

    def reset_password_token_status(self, token):
        return security_reset_password_token_status(token)

    def send_confirmation_instructions(self, user):
        """
        sends signal confirm_instructions_sent
        """
        return security_send_confirmation_instructions(user)

    def send_password_changed_notice(self, user):
        return security_send_password_changed_notice(user)

    def send_password_reset_notice(self, user):
        return security_send_password_reset_notice(user)

    def send_reset_password_instructions(self, user):
        """
        Sends the reset password instructions email for the specified user.

        :param user: The user to send the instructions to
        """
        token = security_generate_reset_password_token(user)
        reset_link = get_url('SECURITY_RESET_PASSWORD_ENDPOINT',
                             token=token, _external=True)

        if app.config.get('SECURITY_SEND_PASSWORD_RESET_EMAIL'):
            security_send_mail(
                subject=app.config.get('SECURITY_EMAIL_SUBJECT_PASSWORD_RESET'),
                recipient=user.email,
                template='reset_instructions', user=user, reset_link=reset_link)

        reset_password_instructions_sent.send(app._get_current_object(),
                                              user=user, token=token)

    def confirm_email_token_status(self, token):
        return security_confirm_email_token_status(token)

    def confirm_user(self, user):
        """Confirms the specified user

        :param user: The user to confirm
        """
        if user.confirmed_at is not None:
            return False
        user.confirmed_at = datetime.now(timezone.utc)
        user.active = True
        if user != current_user:
            self.logout_user()
            self.login_user(user)
        self.session_manager.add(user)
        user_confirmed.send(app._get_current_object(), user=user)
        return True
