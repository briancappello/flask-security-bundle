from flask_security import UserMixin
from flask_security.utils import hash_password as security_hash_password
from flask_sqlalchemy_bundle import db
from flask_unchained import lazy_gettext as _
from .user_role import UserRole


class User(db.Model, UserMixin):
    class Meta:
        lazy_mapped = True

    email = db.Column(db.String(64), unique=True, index=True, info=dict(
        required=_('flask_security_bundle.email_required')))
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
        min_len = 8
        if not password or len(password) < min_len:
            msg = f'Password must be at least {min_len} characters long.'
            raise db.ValidationError(msg)
