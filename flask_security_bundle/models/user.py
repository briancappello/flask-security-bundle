from flask_security import UserMixin
from flask_security.utils import hash_password as security_hash_password

from flask_sqlalchemy_bundle import db

from .user_role import UserRole


class User(db.Model, UserMixin):
    class Meta:
        lazy_mapped = True

    email = db.Column(db.String(64), unique=True, index=True)
    _password = db.Column('password', db.String)
    active = db.Column(db.Boolean(name='active'), default=False)
    confirmed_at = db.Column(db.DateTime(), nullable=True)

    user_roles = db.relationship('UserRole', back_populates='user',
                                 cascade='all, delete-orphan')
    roles = db.association_proxy('user_roles', 'role',
                                 creator=lambda role: UserRole(role=role))

    __repr_props__ = ('id', 'email', 'active')

    def __init__(self, hash_password=True, **kwargs):
        password = kwargs.pop('password', None)
        if password and hash_password:
            self.password = password
        else:
            self._password = password

        super().__init__(**kwargs)

    @db.hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = security_hash_password(password)
