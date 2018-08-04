from flask_login import AnonymousUserMixin
from flask_unchained.bundles.sqlalchemy import db
from flask_unchained import unchained, injectable, lazy_gettext as _
from werkzeug.datastructures import ImmutableList

from .user_role import UserRole
from ..validators import EmailValidator

MIN_PASSWORD_LENGTH = 8


class AnonymousUser(AnonymousUserMixin):
    def __init__(self):
        self.roles = ImmutableList()

    @property
    def id(self):
        return None

    @property
    def active(self):
        return False

    def has_role(self, *args):
        return False


class User(db.Model):
    """
    Base :class:`User` model. Includes :attr:`email`, :attr:`password`, :attr:`active`,
    and :attr:`confirmed_at` columns, and a many-to-many relationship to the
    :class:`Role` model via the intermediary :class:`UserRole` join table.
    """
    class Meta:
        lazy_mapped = True

    email = db.Column(db.String(64), unique=True, index=True, info=dict(
        required=_('flask_security_bundle.email_required'),
        validators=[EmailValidator]))
    _password = db.Column('password', db.String, info=dict(
        required=_('flask_security_bundle.password_required')))
    active = db.Column(db.Boolean(name='active'), default=False)
    confirmed_at = db.Column(db.DateTime(), nullable=True)

    user_roles = db.relationship('UserRole', back_populates='user',
                                 cascade='all, delete-orphan')
    roles = db.association_proxy('user_roles', 'role',
                                 creator=lambda role: UserRole(role=role))

    __repr_props__ = ('id', 'email', 'active')

    @db.hybrid_property
    def password(self):
        return self._password

    @password.setter
    @unchained.inject('security_utils_service')
    def password(self, password, security_utils_service=injectable):
        self._password = security_utils_service.hash_password(password)

    @classmethod
    def validate_password(cls, password):
        if password and len(password) < MIN_PASSWORD_LENGTH:
            raise db.ValidationError(f'Password must be at least '
                                     f'{MIN_PASSWORD_LENGTH} characters long.')

    @unchained.inject('security_utils_service')
    def get_auth_token(self, security_utils_service=injectable):
        """Returns the user's authentication token."""
        return security_utils_service.get_auth_token(self)

    def has_role(self, role):
        """Returns `True` if the user identifies with the specified role.

        :param role: A role name or `Role` instance"""
        if isinstance(role, str):
            return role in (role.name for role in self.roles)
        else:
            return role in self.roles

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False
