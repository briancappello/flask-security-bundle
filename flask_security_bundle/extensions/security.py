from http import HTTPStatus
from flask import Flask, abort, current_app as app
from flask_security import Security as BaseSecurity
from flask_security.core import _context_processor as security_context_processor
from flask_sqlalchemy_bundle import SessionManager

from ..services import UserManager, RoleManager
from ..services._datastore_adapter import DatastoreAdapter


class Security(BaseSecurity):
    def init_app(self, app: Flask):
        self._state = super().init_app(
            app,
            datastore=app.config.get('SECURITY_DATASTORE'),
            login_form=app.config.get('SECURITY_LOGIN_FORM'),
            confirm_register_form=app.config.get('SECURITY_CONFIRM_REGISTER_FORM'),
            register_form=app.config.get('SECURITY_REGISTER_FORM'),
            forgot_password_form=app.config.get('SECURITY_FORGOT_PASSWORD_FORM'),
            reset_password_form=app.config.get('SECURITY_RESET_PASSWORD_FORM'),
            change_password_form=app.config.get('SECURITY_CHANGE_PASSWORD_FORM'),
            send_confirmation_form=app.config.get('SECURITY_SEND_CONFIRMATION_FORM'),
            passwordless_login_form=app.config.get('SECURITY_PASSWORDLESS_LOGIN_FORM'),
            anonymous_user=app.config.get('SECURITY_ANONYMOUS_USER'),
            register_blueprint=False)

        # override the unauthorized action to use abort(401)
        self._state.unauthorized_handler(lambda: abort(HTTPStatus.UNAUTHORIZED))

        # FIXME-mail: register a custom mail task using the mail service
        # self._state.send_mail_task(send_mail_async)

        app.context_processor(security_context_processor)
        app.extensions['security'] = self

    def inject_services(self,
                        user_manager: UserManager,
                        role_manager: RoleManager,
                        session_manager: SessionManager = None):
        self.datastore = DatastoreAdapter(
            user_manager, role_manager, session_manager)

    def __getattr__(self, name):
        """
        The upstream extension is used as a proxy for configuration settings,
        where code sprinkled throughout the flask_security package can reference
        settings by their lowercased name (minus the SECURITY_ prefix) as an
        attribute on the security extension. However, it was built in such a way
        that it caches settings as they were at the time init_app was called,
        without any way to later change them. Which of course is garbage,
        especially for testing, so we need to override __getattr__ so that we
        proxy those requests to app.config
        """
        state_value = getattr(self._state, name, None)
        if name in {'i18n_domain'}:
            return state_value

        try:
            return app.config.get(('SECURITY_' + name).upper(), state_value)
        except RuntimeError:
            raise AttributeError(name)
