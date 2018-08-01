from flask import Flask
from flask_login import LoginManager
from flask_principal import Principal, Identity, UserNeed, RoleNeed, identity_loaded
from flask_unchained import lazy_gettext as _
from flask_unchained.utils import ConfigProperty, ConfigPropertyMeta
from itsdangerous import URLSafeTimedSerializer
from passlib.context import CryptContext
from types import FunctionType

from ..models import AnonymousUser
from ..utils import current_user, verify_hash
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

        # injected services
        self.user_manager = None

        # remaining properties are all set by `self.init_app`
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
        self.confirm_serializer = self._get_serializer(app, 'confirm')
        self.hashing_context = self._get_hashing_context(app)
        self.login_manager = self._get_login_manager(
            app, app.config.get('SECURITY_ANONYMOUS_USER'))
        self.login_manager.id_attribute = 'id'
        self.login_serializer = self._get_serializer(app, 'login')
        self.principal = self._get_principal(app)
        self.pwd_context = self._get_pwd_context(app)
        self.remember_token_serializer = self._get_serializer(app, 'remember')
        self.reset_serializer = self._get_serializer(app, 'reset')

        self.context_processor(lambda: dict(security=_SecurityConfigProperties()))

        identity_loaded.connect_via(app)(self._on_identity_loaded)
        app.extensions['security'] = self

    def inject_services(self, user_manager):
        self.datastore = DatastoreAdapter(user_manager)
        self.login_manager.user_loader(user_manager.get)
        self.user_manager = user_manager

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

    def _get_hashing_context(self, app):
        schemes = app.config.get('SECURITY_HASHING_SCHEMES')
        deprecated = app.config.get('SECURITY_DEPRECATED_HASHING_SCHEMES')
        return CryptContext(
            schemes=schemes,
            deprecated=deprecated)

    def _get_login_manager(self, app, anonymous_user):
        lm = LoginManager()
        lm.anonymous_user = anonymous_user or AnonymousUser
        lm.localize_callback = _
        lm.request_loader(self._request_loader)

        # FIXME: identity
        lm.user_loader(lambda id: self.datastore.get_user(id))

        lm.login_view = 'security_controller.login'
        lm.login_message, _('flask_security_bundle.error.login_required')
        lm.login_message_category = 'info'
        lm.needs_refresh_message = _('flask_security_bundle.error.fresh_login_required')
        lm.needs_refresh_message_category = 'info'
        lm.init_app(app)
        return lm

    def _get_principal(self, app):
        p = Principal(app, use_sessions=False)
        p.identity_loader(self._identity_loader)
        return p

    def _get_pwd_context(self, app):
        pw_hash = app.config.get('SECURITY_PASSWORD_HASH')
        schemes = app.config.get('SECURITY_PASSWORD_SCHEMES')
        deprecated = app.config.get('SECURITY_DEPRECATED_PASSWORD_SCHEMES')
        if pw_hash not in schemes:
            allowed = (', '.join(schemes[:-1]) + ' and ' + schemes[-1])
            raise ValueError(
                "Invalid password hashing scheme %r. Allowed values are %s" %
                (pw_hash, allowed))
        return CryptContext(
            schemes=schemes,
            default=pw_hash,
            deprecated=deprecated)

    def _get_serializer(self, app, name):
        secret_key = app.config.get('SECRET_KEY')
        salt = app.config.get('SECURITY_%s_SALT' % name.upper())
        return URLSafeTimedSerializer(secret_key=secret_key, salt=salt)

    @staticmethod
    def _identity_loader():
        if not isinstance(current_user._get_current_object(), AnonymousUser):
            identity = Identity(current_user.id)
            return identity

    @staticmethod
    def _on_identity_loaded(sender, identity):
        if hasattr(current_user, 'id'):
            identity.provides.add(UserNeed(current_user.id))

        for role in getattr(current_user, 'roles', []):
            identity.provides.add(RoleNeed(role.name))

        identity.user = current_user

    def _request_loader(self, request):
        header_key = self.token_authentication_header
        args_key = self.token_authentication_key
        header_token = request.headers.get(header_key, None)
        token = request.args.get(args_key, header_token)
        if request.is_json:
            data = request.get_json(silent=True) or {}
            token = data.get(args_key, token)

        try:
            data = self.remember_token_serializer.loads(
                token, max_age=self.token_max_age)
            user = self.user_manager.get(data[0])
            if user and verify_hash(data[1], user.password):
                return user
        except:
            pass
        return self.login_manager.anonymous_user()
