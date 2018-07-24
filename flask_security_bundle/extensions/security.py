from flask import Flask
from flask_principal import identity_loaded
from flask_security.core import (
    _get_hashing_context,
    _get_login_manager,
    _get_principal,
    _get_pwd_context,
    _get_serializer,
    _on_identity_loaded,
)
from flask_unchained.utils import ConfigProperty, ConfigPropertyMeta
from types import FunctionType

from ..services._datastore_adapter import DatastoreAdapter


class _SecurityConfigProperties(metaclass=ConfigPropertyMeta):
    __config_prefix__ = 'SECURITY'

    changeable: bool = ConfigProperty()
    confirmable: bool = ConfigProperty()
    login_without_confirmation: bool = ConfigProperty()
    recoverable: bool = ConfigProperty()
    registerable: bool = ConfigProperty()
    trackable: bool = ConfigProperty()

    token_authentication_header: str = ConfigProperty()
    token_authentication_key: str = ConfigProperty()
    token_max_age: str = ConfigProperty()

    password_hash: str = ConfigProperty()
    password_salt: str = ConfigProperty()

    datetime_factory: FunctionType = ConfigProperty()
    _unauthorized_callback: FunctionType = \
        ConfigProperty('SECURITY_UNAUTHORIZED_CALLBACK')


class Security(_SecurityConfigProperties):
    def __init__(self):
        self._context_processors = {}
        self._send_mail_task = None

        # properties set by init_app:
        self.confirm_serializer = None
        self.datastore = None
        self.hashing_context = None
        self.login_manager = None
        self.login_serializer = None
        self.principal = None
        self.pwd_context = None
        self.remember_token_serializer = None
        self.reset_serializer = None

    def init_app(self, app: Flask):
        self.confirm_serializer = _get_serializer(app, 'confirm')
        self.hashing_context = _get_hashing_context(app)
        self.login_manager = _get_login_manager(
            app, app.config.get('SECURITY_ANONYMOUS_USER'))
        self.login_serializer = _get_serializer(app, 'login')
        self.principal = _get_principal(app)
        self.pwd_context = _get_pwd_context(app)
        self.remember_token_serializer = _get_serializer(app, 'remember')
        self.reset_serializer = _get_serializer(app, 'reset')

        self.context_processor(lambda: dict(security=_SecurityConfigProperties()))

        identity_loaded.connect_via(app)(_on_identity_loaded)
        app.extensions['security'] = self

    def inject_services(self, user_manager, role_manager, session_manager=None):
        self.datastore = DatastoreAdapter(
            user_manager, role_manager, session_manager)

    def context_processor(self, fn):
        self._add_ctx_processor(None, fn)

    def forgot_password_context_processor(self, fn):
        self._add_ctx_processor('forgot_password', fn)

    def login_context_processor(self, fn):
        self._add_ctx_processor('login', fn)

    def register_context_processor(self, fn):
        self._add_ctx_processor('register', fn)

    def reset_password_context_processor(self, fn):
        self._add_ctx_processor('reset_password', fn)

    def change_password_context_processor(self, fn):
        self._add_ctx_processor('change_password', fn)

    def send_confirmation_context_processor(self, fn):
        self._add_ctx_processor('send_confirmation', fn)

    def send_login_context_processor(self, fn):
        self._add_ctx_processor('send_login', fn)

    def mail_context_processor(self, fn):
        self._add_ctx_processor('mail', fn)

    def _add_ctx_processor(self, endpoint, fn):
        group = self._context_processors.setdefault(endpoint, [])
        fn not in group and group.append(fn)

    def _run_ctx_processor(self, endpoint):
        rv = {}
        for group in [None, endpoint]:
            for fn in self._context_processors.setdefault(group, []):
                rv.update(fn())
        return rv
