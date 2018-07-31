from flask_security import UserMixin
from flask_security.utils import hash_password as security_hash_password
from flask_unchained.bundles.sqlalchemy import db
from flask_unchained import lazy_gettext as _

from .user_role import UserRole
from ..validators import EmailValidator

MIN_PASSWORD_LENGTH = 8


class User(db.Model, UserMixin):
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
    def password(self, password):
        self._password = security_hash_password(password)

    @classmethod
    def validate_password(cls, password):
        if password and len(password) < MIN_PASSWORD_LENGTH:
            raise db.ValidationError(f'Password must be at least '
                                     f'{MIN_PASSWORD_LENGTH} characters long.')
